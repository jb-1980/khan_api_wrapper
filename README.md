# KhanAPI (Python 3 Wrapper for Khan Academy API)
===============

## About
This is a simple implementation of using the Khan Academy API with python. It uses the alternative method of logging in with your own account, and should be sufficient if you are only looking to retrieve data from your students.

#### Set up:

clone this repository:

```
$ git clone git@github.com:jb-1980/KhanAPI.git
$ cd KhanAPI
```
install dependencies:
```
$ pip install -r requirements.txt
```


[Register your app with Khan Academy](https://www.khanacademy.org/api-apps/register), then update `config.py.template` with your tokens and credentials, and save as `config.py`. That is it, you should now be able to use the wrapper in your python script.

#### General use:
test in an interactive shell:

```
$ python
> from khan import KhanAcademySignIn, KhanAPI
>
> kauth = KhanAcademySignIn()
> token, secret = kauth.authenticate_self()
>
> kapi = KhanApi(token, secret)
> kapi.user() # should print your user data to console.
>
> # Use your own endpoint
> kapi.get("/api/internal/user/missions") # should show your missions
```

See `example.py` for ideas on how to integrate into your own project, and examine `khan.py` for all the available methods.

#### Token freshness:

Through trial I have discovered that the access token and secret are valid for 2 weeks. So you may consider storing them in a separate file or database, and write a function to only fetch tokens if they are expired.

```
def get_tokens():
    # fetch token data from saved json file
    with open('tokens.json', 'r') as f:
        tokens = json.loads(f)

    # check if tokens are expired
    now = time.time()
    if now - tokens["timestamp"] > 3600 * 24 * 14:
        token, secret = kauth.authorize_self()

        # update file with new tokens and timestamp
        with open('tokens.json', 'w') as t:
            t.write(json.dumps({
              "token": token,
              "secret": secret,
              "timestamp": now,
            }))

        # return fresh tokens
        return token, secret

    # tokens are still valid, so return them
    return tokens["token"], tokens["secret"]

# Then use the function to ensure we only use fresh tokens
token, secret = get_Tokens()
kapi = KhanAPI(token, secret)
...
```
