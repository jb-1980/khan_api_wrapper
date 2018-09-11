from khan import KhanAcademySignIn, KhanAPI
from pprint import pprint

# First authenticate with Khan Academy. This will only work for the account
# used to register the app, and if the account settings are set up in config.py
kauth = KhanAcademySignIn()
token, secret = kauth.authorize_self()

# Now instatiate the authenticated khan api class, which can be used to fetch
# protected endpoints
kapi = KhanAPI(token, secret)

# Fetch data from documented api call
user = kapi.get_user_profile()
# pprint(user)

# Fetch data from undocumented api call. Use these cautiously as they are not
# garaunteed to work. See https://github.com/Khan/khan-api/wiki/Khan-Academy-API-Authentication#the-endpoints-exposed-on-the-api-explorer-dont-seem-to-do-what-i-need-am-i-ableallowed-to-access-any-other-endpoints
students = kapi.get_student_list()
# pprint(students)

# Access the get function directly to use an endpoint of your choice
missions = kapi.get("/api/internal/user/missions")
# pprint(missions)
