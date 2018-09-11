from khan import KhanAcademySignIn, KhanAPI
from pprint import pprint
from datetime import datetime

# First authenticate with Khan Academy. This will only work for the account
# used to register the app, and if the account settings are set up in config.py
kauth = KhanAcademySignIn()
token, secret = kauth.authorize_self()

# Now instatiate the authenticated khan api class, which can be used to fetch
# protected endpoints
kapi = KhanAPI(token, secret)

# Fetch data from documented api call
user = kapi.user()
# pprint(user)

# Fetch data from undocumented api call. Use these cautiously as they are not
# garaunteed to work. See https://github.com/Khan/khan-api/wiki/Khan-Academy-API-Authentication#the-endpoints-exposed-on-the-api-explorer-dont-seem-to-do-what-i-need-am-i-ableallowed-to-access-any-other-endpoints
params = {
    "dt_start": "1970-09-08T07:00:00.000Z",
    "dt_end": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
}
students = kapi.get_student_list(params)
# pprint(students)

# Access the get function directly to use an endpoint of your choice
missions = kapi.get("/api/internal/user/missions")
# pprint(missions)
