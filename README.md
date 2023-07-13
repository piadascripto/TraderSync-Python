# Python Flask ReplAuth

Using the ReplAuth with Flask is super easy! First we create a new Flask app: 

<details>
  <summary>Import Flask and create new Flask app</summary>

```python
from flask import Flask, render_template, request
app = Flask('app')
@app.route('/')
```
</details>

And then we request the headers: 

<details>
  <summary>Requested Headers:</summary>

```python
def hello_world():
    print(request.headers)
    return render_template(
        'index.html',
        user_id=request.headers['X-Replit-User-Id'],
        user_name=request.headers['X-Replit-User-Name'],
        user_roles=request.headers['X-Replit-User-Roles'],
        user_bio=request.headers['X-Replit-User-Bio'],
        user_profile_image=request.headers['X-Replit-User-Profile-Image'],
        user_teams=request.headers['X-Replit-User-Teams'],
        user_url=request.headers['X-Replit-User-Url']
    )
```
</details>

In this code we've requested all the possible headers, which are these:

<details>
  <summary>All Replit Headers</summary>

```python
X-Replit-User-Bio
X-Replit-User-Id
X-Replit-User-Name
X-Replit-User-Profile-Image
X-Replit-User-Roles
X-Replit-User-Teams
X-Replit-User-Url
```
</details>

Once we've requested all these headers, we can show the information we've got after the user has passed through the Auth. This info will be displayed on the console, but can also be displayed in a html file.

We can show this by displaying the variable assigned to a header in a HTML tag (it can also be shown without a tag). If we wanted to show the username of the user we would put this:

```html
<h1>{{ user_name }}</h1>
```

And the output will be a heading (h1) with the username. 

# ReplAuth FAQ 

The question is in a quote and in italic and the answer is in a bullet point.

<details>
  <summary>ReplAuth FAQ</summary>
  
  > *How many ReplAuths are there?*
  
  - There are 2 repl auths!
 ---
  > *Which ReplAuths are there?*
  
  - Node.js and Python Flask
---
  > *Is there a Replit Documentation on ReplAuths?*

  - Yes! You can find it in the [Replit Docs](https://docs.replit.com)
</details>

# Template

**Name**: Python Flask ReplAuth

**Description**: Python Flask ReplAuth is easy and useful to use! What are you waiting for? Start using ReplAuth today!

# Questions?

If you have any question please look at our support resources:

- [Replit Docs](https://docs.replit.com)
- [Ask forum](https://ask.replit.com)
