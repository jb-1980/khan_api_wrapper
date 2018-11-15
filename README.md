# khan_api_wrapper (Python 3 Wrapper for [Khan Academy API](https://github.com/Khan/khan-api))
------------------------------------------------

## About
This is a simple implementation of using the Khan Academy API with python. It uses the alternative method of logging in with your own account, and should be sufficient if you are only looking to retrieve data from your students.

#### Requires
* requests
* rauth

#### Set up:

Install:

```
$ pip install khan_api_wrapper
```
[Register your app with Khan Academy](https://www.khanacademy.org/api-apps/register), to get the necessary tokens. That is it, you should now be able to use the wrapper in your python script.

#### General use:
test in an interactive shell:

```python
$ python
> from khan_api_wrapper.khan import KhanAcademySignIn, KhanAPI
>
> consumer_key = "Key from registering app"
> consumer_token = "Token from registering app"
> khan_identifier = "username_of_account_used_to_register_app"
> khan_password = "password_of_account_used_to_register_app"
> kauth = KhanAcademySignIn(consumer_key, consumer_token, khan_identifier, khan_password)
> token, secret = kauth.authenticate_self()
>
> kapi = KhanApi(consumer_key, consumer_token, token, secret)
> kapi.user() # should print your user data to console.
>
> # Use your own endpoint
> kapi.get("/api/internal/user/missions") # should show your missions
```

Examine `khan.py` for all the available methods or `example.py` for ideas on how to use in your application.

#### Token freshness:

Through trial I have discovered that the access token and secret are valid for 2 weeks. So you may consider storing them in a separate file or database, and write a function to only fetch tokens if they are expired.

```python
def get_tokens():

    # fetch token data from saved json file
    with open("tokens.json", "r") as f:
        tokens = json.loads(f.read())

    # check if tokens are expired
    now = time.time()
    if now - tokens["timestamp"] > 3600 * 24 * 14:
        kauth = KhanAcademySignIn(consumer_key, consumer_secret, token, uname, pwd)
        token, secret = kauth.authorize_self()

        # update file with new tokens and timestamp
        with open("tokens.json", "w") as t:
            t.write(
                json.dumps({"token": token, "secret": secret, "timestamp": now})
            )

        # return fresh tokens
        return token, secret

    # tokens are still valid, so return them
    return tokens["token"], tokens["secret"]

# Then use the function to ensure we only use fresh tokens when necessary
token, secret = get_tokens()
kapi = KhanAPI(consumer_key, consumer_secret, token, secret)
...
```
