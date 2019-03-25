from rauth import OAuth1Service
from time import time
import json
import requests
from khan_api_wrapper import graphql_schema as gql


SERVER_URL = "http://www.khanacademy.org"
REQUEST_TOKEN_URL = SERVER_URL + "/api/auth2/request_token"
ACCESS_TOKEN_URL = SERVER_URL + "/api/auth2/access_token"
AUTHORIZE_URL = SERVER_URL + "/api/auth2/authorize"
BASE_URL = SERVER_URL + "/api/auth2"


class KhanAcademySignIn:
    """
    Class to set up the rauth service and use it to retrieve the access tokens
    """

    def __init__(self, consumer_key, consumer_secret, khan_identifier, khan_password):
        self.service = OAuth1Service(
            name="Grade Syncer",
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            request_token_url=REQUEST_TOKEN_URL,
            access_token_url=ACCESS_TOKEN_URL,
            authorize_url=AUTHORIZE_URL,
            base_url=BASE_URL,
        )
        self.khan_identifier = khan_identifier
        self.khan_password = khan_password

    ## Only going to implement the ability to authorize with the credentials
    ## of the account used to create the app. This has the benefit of avoiding
    ## all the extra steps of using browser based authentication. A more
    ## complete class can be seen at
    ## https://github.com/jb-1980/mission-control/blob/master/app/oauth.py
    def authorize_self(self):
        # Get token and secret
        request_token, request_token_secret = self.service.get_request_token(
            method="POST"
        )

        # Authorize token by logging into your own account
        data = {
            "oauth_token": request_token,
            "identifier": self.khan_identifier,
            "password": self.khan_password,
        }

        # Posting to the authorize url will then authenticate the request token
        # and secret, and make available the retrieval of the access token and
        # secret
        requests.post(AUTHORIZE_URL, data=data)

        # Get access token and secret
        oauth_session = self.service.get_auth_session(
            request_token, request_token_secret
        )

        # Now we give the user the access token and secret as a tuple
        return oauth_session.access_token, oauth_session.access_token_secret


class KhanAPI:
    """
    Basic api class to access the Khan Academy api. If instantiated with a token
    and secret it will allow for authenticated endpoints. More endpoints could
    be added to align with those found at https://api-explorer.khanacademy.org/
    """

    def __init__(
        self,
        consumer_key=None,
        consumer_secret=None,
        access_token=None,
        access_token_secret=None,
    ):
        self.authorized = False
        # We need an access token and secret to make authorized calls
        # Otherwise we can only access open endpoints
        if access_token and access_token_secret:
            if consumer_key == None or consumer_secret == None:
                raise ValueError(
                    "consumer_key and consumer_secret must be provided if access tokens are provided"
                )
            self.service = OAuth1Service(
                name="khan_oauth",
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                request_token_url=REQUEST_TOKEN_URL,
                access_token_url=ACCESS_TOKEN_URL,
                authorize_url=AUTHORIZE_URL,
                base_url=BASE_URL,
            )
            self.session = self.service.get_session((access_token, access_token_secret))
            self.authorized = True
        self.get_resource = self.get

    def get(self, url, params={}):
        if self.authorized:
            response = self.session.get(SERVER_URL + url, params=params)
            try:
                return response.json()
            except ValueError:
                # Checking if it was a server error, in which case we will let
                # the programmer deal with a workaround. Otherwise, print the
                # response details to the console for debugging.
                if response.status_code == 500:
                    print("500 error receieved. You should do something with it!")
                    return {"error": 500}
                print("#" * 50)
                print("Status Code: ", response.status_code)
                print("Content-Type: ", response.headers["content-type"])
                print("Text:")
                print(response.text)
                print("#" * 50)
                raise

        else:

            return requests.get(SERVER_URL + url, params=params).json()

    def post(self, url, params, data, headers=None):
        if headers:
            response = self.session.post(
                SERVER_URL + url, data=data, params=params, headers=headers
            )
        else:
            response = self.session.post(SERVER_URL + url, data=data, params=params)
        try:
            return response.json()
        except ValueError:
            # Checking if it was a server error, in which case we will let
            # the programmer deal with a workaround. Otherwise, print the
            # response details to the console for debugging.
            if response.status_code == 500:
                print("500 error receieved. You should do something with it!")
                print(response.text)
                return {"error": 500}
            print("#" * 50)
            print("Status Code: ", response.status_code)
            print("Content-Type: ", response.headers["content-type"])
            print("Text:")
            print(response.text)
            print("#" * 50)
            raise

    ############################################################################
    ############ THE FIRST SECTION IS THE DOCUMENTED API AS FOUND AT  ##########
    ############ https://api-explorer.khanacademy.org/                ##########

    # BADGES
    def badges(self, params={}):
        """
        Retrieve a list of all badges. If authenticated, badges that have been
        earned by the specified user will contain extra UserBadge information.
        :param: params: one of four identifiers:
          username,
          kaid,
          userid,
          email
        """
        return self.get_resource("/api/v1/badges", params=params)

    def badges_categories(self):
        """Retrieve a list of all badge categories"""
        return self.get_resource("/api/v1/badges/categories")

    def badges_categories_category(self, category_id):
        """Retrieve specific badge category identified by <category>.
        :param: category_id: An integer representing the category:
          '0' for 'meteorite',
          '1' for 'moon',
          '2' for 'earth',
          '3' for 'sun',
          '4' for 'black hole',
          '5' for 'challenge patch'
        """
        return self.get_resource("/api/v1/badges/categories/" + category_id)

    # EXERCISES
    def exercises(self, tags=[]):
        """Retrieve a filtered list of exercises in the library.
        :param: tags, A comma-separated list of tags to filter on
        """
        return self.get_resource("/api/v1/exercises", params={"tags": tags})

    def exercises_exercise_name(self, name):
        """Retrieve exercise identified by <name>"""
        return self.get_resource("/api/v1/exercises/" + name)

    def exercises_exercise_followup_exercises(self, name):
        """Retrieve all the exercises that list <name> as a prerequisite."""
        return self.get_resource("/api/v1/exercises/%s/followup_exercises" % name)

    def exercises_exercise_videos(self, name):
        """Retrieve a list of all videos associated with <name>."""
        return self.get_resource("/api/v1/exercises/%s/videos" % name)

    def exercises_perseus_autocomplete(self):
        """listing of Perseus exercises used for autocomplete."""
        return self.get_resource("/api/v1/exercises/perseus_autocomplete")

    # PLAYLISTS
    def playlists_exercises(self, topic_slug):
        """Retrieve a list of all exercises in the topic id'ed by <topic_slug>."""
        return self.get_resource("/api/v1/playlists/%s/exercises" % topic_slug)

    def playlists_videos(self, topic_slug):
        """Retrieve a list of all videos in the topic id'ed by <topic_slug>."""
        return self.get_resource("/api/v1/playlists/%s/videos" % topic_slug)

    # TOPIC
    def topic(self, topic_slug):
        """Return info about a node in the topic-tree, including its children."""
        return self.get_resource("/api/v1/topic/" + topic_slug)

    def topic_exercises(self, topic_slug):
        """Retrieve a list of all exercises in the topic id'ed by <topic_slug>"""
        return self.get_resource("/api/v1/topic/%s/exercises" % topic_slug)

    def topic_videos(self, topic_slug):
        """Retrieve a list of all videos in the topic identified by <topic_slug>."""
        return self.get_resource("/api/v1/topic/%s/videos" % topic_slug)

    # TOPICTREE
    def topictree(self, kind=None):
        """Retrieve full hierarchical listing of our entire library's topic tree.
        :param: kind, string of topic type
            kind=Topic, returns only topics
            kind=Exercise, returns topics and exercises
        """
        return self.get_resource("/api/v1/topictree", params={"kind": kind})

    # USER. All User methods require authentication
    def user(self, identifier={}):
        """Retrieve data about a user. If no identifier is provided, it will
        return the authenticated user.
        :param: identifier, one of three identifiers:
          username, userid, email
        """
        return self.get_resource("/api/v1/user", params=identifier)

    def user_exercises(self, identifier={}, exercises=[]):
        """Retrieve info about a user's interaction with exercises.
        :param: identifier, one of four identifiers: username, userid, email, kaid
        :param: exercises, optional list of exercises to filter. If none is provided,
        all exercises attempted by user will be returned."""
        return self.get_resource(
            "/api/v1/user/exercises", params={"exercises": exercises, **identifier}
        )

    def user_exercises_name(self, exercise, identifier={}):
        """Retrieve info about a specific exercise engaged by a specific user
        identified with the name and identifier
        :param: exercise, the specific exercise to get info for
        :param: identifier, one of four identifiers: username, userid, email, kaid
        """
        return self.get_resource(
            "/api/v1/user/exercises/" + exercise, params=identifier
        )

    def user_exercises_followup_exercises(self, exercise, indentifier={}):
        """Retrieve info about all specific exercise listed as a prerequisite to
        <exercise_name>
        :param: exercise, the specific exercise to get info for
        :param: identifier, one of four identifiers: username, userid, email, kaid
        """
        return self.get_resource(
            "/api/v1/user/exercises/%s/followup_exercises" % exercise_name,
            params=identifier,
        )

    def user_exercises_log(self, exercise, params={}):
        """
        Retrieve a list of ProblemLog entities for one exercise for one user.
        """
        return self.get_resource("/api/v1/user/exercises/%s/log" % exercise, params)

    def user_exercises_progress_changes(self, exercise, params={}):
        """
        Retrieve a list of ProblemLog entities for one exercise for one user.
        """
        return self.get_resource(
            "/api/v1/user/exercises/%s/progress_changes" % exercise, params
        )

    # TODO Finish implementing the user methods

    # VIDEOS
    # TODO implement the videos methods

    ############################################################################
    #######  Personal API methods, many using the internal api            ######
    #######  While Khan Academy does not discourage using these endpoints ######
    #######  they warn that they may break without notice.                ######
    ############################################################################
    def get_mission(self, mission):
        """
        Retrieve the mission topics and skills for the given mission
        """
        return self.get_resource("/api/internal/user/mission/" + mission)

    def get_progress_info(self, params={}):
        return self.get_resource("/api/internal/user/missions/progress_info", params)

    def get_missions(self, params={}):
        return self.get_resource("/api/internal/user/missions", params)

    def get_student_list(self, params={}):
        r = self.get_resource("/api/internal/user/students/progress", params)
        return r["students"]

    def get_student_progress(self, kaid, params={}):
        endpoint = "/api/internal/user/{}/progress".format(kaid)
        response = self.get_resource(endpoint, params)
        if "students" in response:
            return response["students"][0]
        return response

    def get_all_math_exercises(self):
        """
        This is an internal method found by watching network calls on the
        Khan Academy. Khan Academy warns that while using such methods is
        permitted, they may change without warning.
        This is a way to get the basic exercise meta data as well as topic
        structure. It has a lot smaller footprint that get_all_exercises.
        """
        return self.get_resource("/api/internal/exercises/math_topics_and_exercises")

    def get_many_exercises(self, exercises, kaid):
        """
        Since the api restricts the url length to 2048 characters, and making a
        request for many exercises will often exceed this limit, this function will
        truncate the url below the limit, and tie the responses together.
        This function fetches as exercise1,exercise2,... instead of
        exercise=exercise1&exercise=exercise2,...
        """
        exercises.sort()
        out = []
        tmp_lst = []
        params = {"exercises": [], "kaid": kaid}
        while exercises:
            s = ""
            tmp_lst = []
            for exercise in exercises:
                t = s + "," + exercise
                if len(t) < 1500:
                    s += "," + exercise
                    tmp_lst.append(exercise)
                else:
                    break
            exercises = [x for x in exercises if x not in tmp_lst]
            url = "/api/v1/user/exercises"
            params["exercises"] = ",".join(tmp_lst)
            response = self.get_resource(url, params)
            data = response
            for datum in data:
                out.append(datum)
        return out

    def join_class(class_code):
        """
        endpoint to join a class by the class code
        """
        endpoint = "/api/internal/user/joinclass/%s" % class_code
        return self.get_resource(endpoint)

    ############################################################################
    ###  GRAPHQL endpoints  ####################################################
    ############################################################################

    def post_graphql(self, params={}, data={}):
        """
        Retrieve resources using the graphql schema
        """
        headers = {"content-type": "application/json"}

        return self.post("/api/internal/graphql", params, data, headers)

    # QUERIES

    def simple_completion_query(self, assignment_id):
        data = {
            "operationName": "simpleCompletionQuery",
            "variables": {"assignmentId": assignment_id},
            "query": gql.simpleCompletionQuery,
        }

        params = {"lang": "en", "_": round(time() * 1000)}

        return self.post_graphql(params, json.dumps(data))

    def get_students_list(self, hasClassId=False, classId="", pageSize=1000):
        data = {
            "operationName": "getStudentsList",
            "variables": {
                "hasClassId": hasClassId,
                "classId": classId,
                "pageSize": pageSize,
            },
            "query": gql.getStudentsList,
        }

        params = {"lang": "en", "_": round(time() * 1000)}

        return self.post_graphql(params, json.dumps(data))

    def get_progress_by_student(self, class_id):

        data = {
            "operationName": "ProgressByStudent",
            "query": gql.progressByStudent,
            "variables": {
                "classId": class_id,
                "assignmentFilters": {"dueAfter": None, "dueBefore": None},
                "contentKinds": None,
                "pageSize": None,
            },
        }

        params = {"lang": "en", "_": round(time() * 1000)}

        return self.post_graphql(params, json.dumps(data))

    def auto_assignable_students(self, student_list_id):

        data = {
            "operationName": "AutoAssignableStudents",
            "query": gql.AutoAssignableStudents,
            "variables": {"studentListId": student_list_id},
        }

        params = {
            "lang": "en",
            "_": round(time() * 1000),
            "opname": "AutoAssignableStudents",
        }

        return self.post_graphql(params, json.dumps(data))

    def coach_assignments(self, student_list_id, **kwargs):
        """
        Retrieve a list of all the assignments for a course and their meta data
        Optional params to assist in filtering:
            dueAfter: ISO 8601 datestring, like "2019-01-08T06:59:59.999Z"
            dueBefore: ISO 8601 datestring, like "2019-01-08T06:59:59.999Z",
            isDraft: Boolean,
            orderBy: String of type "DUE_DATE_ASC",
            pageSize: Int 
        """
        data = {
            "operationName": "CoachAssignments",
            "query": gql.CoachAssignments,
            "variables": {
                "after": None,
                "assignmentFilters": {
                    "dueAfter": kwargs.get("dueAfter"),
                    "dueBefore": kwargs.get("dueBefore"),
                    "isDraft": kwargs.get("isDraft", False),
                },
                "dueAfter": kwargs.get("dueAfter"),
                "dueBefore": kwargs.get("dueBefore"),
                "isDraft": kwargs.get("isDraft", False),
                "orderBy": kwargs.get("orderBy", "DUE_DATE_ASC"),
                "pageSize": kwargs.get("pageSize", 100),
                "studentListId": student_list_id,
            },
        }

        params = {"lang": "en", "_": round(time() * 1000), "opname": "CoachAssignments"}

        return self.post_graphql(params, json.dumps(data))

    def quiz_unit_test_attempts_query(self, topic_id, **kwargs):
        """
        Get the progress of the logged in user of quiz and unit tests for the
        given topic id. 
        """
        data = {
            "operationName": "quizAndUnitTestAttemptsQuery",
            "query": gql.quizAndUnitTestAttemptsQuery,
            "variables": {"topicId": topic_id},
        }

        params = {
            "lang": "en",
            "_": round(time() * 1000),
            "opname": "quizAndUnitTestAttemptsQuery",
        }

        return self.post_graphql(params, json.dumps(data))

    # MUTATIONS

    def stop_coaching(self, kaids):
        """
        A method to remove inactive students from being coached.
        :param: kaids, list of kaids you want to stop coaching
        """
        data = {
            "operationName": "stopCoaching",
            "variables": {"coachRequestIds": [], "invitationIds": [], "kaids": kaids},
            "query": gql.stopCoaching,
        }

        params = {"lang": "en", "_": round(time() * 1000)}

        return self.post_graphql(params, json.dumps(data))

    def transfer_students(self, fromListIds, toListIds, kaids):
        """
        A method to add or remove students from a course
        :param: fromListIds, a list of course ids being transferred from
        :param: toListIds, a list of course ids that kaids is being transferred to
        :param: kaids, list of kaids that are being transferred
        if toListIds = [], will remove kaids from the course
        """
        data = {
            "operationName": "transferStudents",
            "variables": {"coachRequestIds": [], "invitationIds": [], "kaids": kaids},
            "query": gql.transferStudents,
        }

        params = {"lang": "en", "_": round(time() * 1000)}

        return self.post_graphql(params, json.dumps(data))

    def update_auto_assign(self, student_list_id, student_kaids, auto_assign=True):
        """
        A method to update the list of assignments to include students who have
        recently been enrolled in the course.
        :param: student_list_id, course id from khan academy
        :param: student_kaids, a list of kaids for students being included
        :param: auto_assign, boolean to determine if these students should be included
        """
        data = {
            "operationName": "updateAutoAssign",
            "query": gql.updateAutoAssign,
            "variables": {
                "studentListId": student_list_id,
                "studentKaids": student_kaids,
                "autoAssign": auto_assign,
            },
        }

        params = {"lang": "en", "_": round(time() * 1000), "opname": "updateAutoAssign"}

        return self.post_graphql(params, json.dumps(data))

    def publish_assignment(self, assignment_id):
        """
        A method to move an assignment from saved to active
        :param: assignment_id, int id of assignment from from khan academy, list
        of saved assignment ids can be found using coach_assignments method, passing
        isDraft=True keyword.
        """
        data = {
            "operationName": "publishAssignment",
            "query": gql.publishAssignment,
            "variables": {"assignmentId": assignment_id},
        }

        params = {
            "lang": "en",
            "_": round(time() * 1000),
            "opname": "publishAssignment",
        }

        return self.post_graphql(params, json.dumps(data))

