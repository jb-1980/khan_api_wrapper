from rauth import OAuth1Service
from time import time
import json
import requests

try:
    from config import (
        CONSUMER_KEY,
        CONSUMER_SECRET,
        KHAN_IDENTIFIER,
        KHAN_PASSWORD,
    )
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "config.py not found! Did you set the variables in config.py.template and change the name to config.py?"
    )

SERVER_URL = "http://www.khanacademy.org"
REQUEST_TOKEN_URL = SERVER_URL + "/api/auth2/request_token"
ACCESS_TOKEN_URL = SERVER_URL + "/api/auth2/access_token"
AUTHORIZE_URL = SERVER_URL + "/api/auth2/authorize"
BASE_URL = SERVER_URL + "/api/auth2"

# TODO Add a method that will allow general authorization. It will require setting
# up a callback server, and then responding to that callback. A more complete
# class can be seen at https://github.com/jb-1980/mission-control/blob/master/app/oauth.py
class KhanAcademySignIn:
    """
    Class to set up the rauth service and use it to retrieve the access tokens
    """

    def __init__(self):
        self.service = OAuth1Service(
            name="Grade Syncer",
            consumer_key=CONSUMER_KEY,
            consumer_secret=CONSUMER_SECRET,
            request_token_url=REQUEST_TOKEN_URL,
            access_token_url=ACCESS_TOKEN_URL,
            authorize_url=AUTHORIZE_URL,
            base_url=BASE_URL,
        )

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
            "identifier": KHAN_IDENTIFIER,
            "password": KHAN_PASSWORD,
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

    def __init__(self, access_token=None, access_token_secret=None):
        self.authorized = False
        # We need an access token and secret to make authorized calls
        # Otherwise we can only access open endpoints
        if access_token and access_token_secret:
            self.service = OAuth1Service(
                name="khan_oauth",
                consumer_key=CONSUMER_KEY,
                consumer_secret=CONSUMER_SECRET,
                request_token_url=REQUEST_TOKEN_URL,
                access_token_url=ACCESS_TOKEN_URL,
                authorize_url=AUTHORIZE_URL,
                base_url=BASE_URL,
            )
            self.session = self.service.get_session(
                (access_token, access_token_secret)
            )
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
                    print(
                        "500 error receieved. You should do something with it!"
                    )
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
            response = self.session.post(
                SERVER_URL + url, data=data, params=params
            )
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
        return self.get_resource(
            "/api/v1/exercises/%s/followup_exercises" % name
        )

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
        :param: identifier, on of four identifiers: username, userid, email, kaid
        :param: exercises, optional list of exercises to filter. If none is provided,
        all exercises attempted by user will be returned."""
        return self.get_resource(
            "/api/v1/user/exercises",
            params={"exercises": exercises, **identifier},
        )

    def user_exercises_log(self, exercise, params={}):
        """
        Retrieve a list of ProblemLog entities for one exercise for one user.
        """
        return self.get_resource(
            "/api/v1/user/exercises/%s/log" % exercise, params
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
        return self.get_resource(
            "/api/internal/user/missions/progress_info", params
        )

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
        return self.get_resource(
            "/api/internal/exercises/math_topics_and_exercises"
        )

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
        params = {"exercises": []}
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

    def post_graphql(self, params={}, data={}):
        """
        Retrieve resources using the graphql schema
        """
        headers = {"content-type": "application/json"}

        return self.post("/api/internal/graphql", params, data, headers)

    def simple_completion_query(self, assignment_id):
        data = {
            "operationName": "simpleCompletionQuery",
            "variables": {"assignmentId": assignment_id},
            "query": """query simpleCompletionQuery($assignmentId: String!) {\n  coach {\n    id\n    assignment(id: $assignmentId) {\n      assignedDate\n      dueDate\n      id\n      itemCompletionStates {\n        student {\n          id\n          kaid\n          coachNickname\n          profileRoot\n          __typename\n        }\n        state\n        completedOn\n        bestScore {\n          numCorrect\n          numAttempted\n          __typename\n        }\n        exerciseAttempts {\n          id\n          isCompleted\n          numAttempted\n          numCorrect\n          lastAttemptDate\n          __typename\n        }\n        content {\n          id\n          translatedTitle\n          defaultUrlPath\n          kind\n          __typename\n        }\n        __typename\n      }\n      studentList {\n        id\n        name\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n""",
        }

        params = {"lang": "en", "_": round(time() * 1000)}

        return self.post_graphql(params, json.dumps(data))
