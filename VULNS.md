
[comment]: # (Generated from JSON file by generate_vulns_md.py)
[comment]: # (Intended to be read in GitHub's markdown renderer. Apologies if the plaintext formatting is messy.)

# OWASP Falihax Vulnerabilities
*General hackathon feedback by [CyberSoc](https://cybersoc.org.uk/?r=falihax-vulns)*

A list of known vulnerabilites in the OWASP "Falihax" hackathon web app. This is a collection of vulnerabilities found by those who took part and some that noone found! This list isn't exhaustive - if you find more vulnerabilites then let us know and we'll add them to this list!

This is general feedback - for your specific feedback and points total, see your own repository!

## Table of Contents
* [OWASP A01: Broken Access Control](#owasp-a01-broken-access-control)
    - [A01-01: Unauthorised users are allowed to visit secure pages](#a01-01-unauthorised-users-are-allowed-to-visit-secure-pages)
    - [A01-02: No access control/owner check on account page](#a01-02-no-access-control/owner-check-on-account-page)
    - [A01-03: No access control on the admin page](#a01-03-no-access-control-on-the-admin-page)
* [OWASP A02: Cryptographic Failures](#owasp-a02-cryptographic-failures)
    - [A02-01: Unsuitable use of ROT-13 "encryption"](#a02-01-unsuitable-use-of-rot-13-encryption)
    - [A02-02: Random number generation is not secure](#a02-02-random-number-generation-is-not-secure)
* [OWASP A03: Injection](#owasp-a03-injection)
    - [A03-01: SQL Injection](#a03-01-sql-injection)
* [OWASP A04: Insecure Design](#owasp-a04-insecure-design)
    - [A04-01: No CAPTCHAs Used](#a04-01-no-captchas-used)
    - [A04-02: No Password Strength Checks](#a04-02-no-password-strength-checks)
    - [A04-03: No Rate Limiting](#a04-03-no-rate-limiting)
    - [A04-04: Vulnerable to MITM attack](#a04-04-vulnerable-to-mitm-attack)
* [OWASP A05: Security Misconfiguration](#owasp-a05-security-misconfiguration)
    - [A05-01: Flask secret key used is not secure](#a05-01-flask-secret-key-used-is-not-secure)
    - [A05-02: Flask debug mode is left enabled](#a05-02-flask-debug-mode-is-left-enabled)
* [OWASP A06: Vulnerable and Outdated Components](#owasp-a06-vulnerable-and-outdated-components)
* [OWASP A07: Identification and Authentication Failures](#owasp-a07-identification-and-authentication-failures)
    - [A07-01: No multi-factor authentication available](#a07-01-no-multi-factor-authentication-available)
* [OWASP A08: Software and Data Integrity Failures](#owasp-a08-software-and-data-integrity-failures)
    - [A08-01: Missing Validation for Lower Bound of Transaction Amount](#a08-01-missing-validation-for-lower-bound-of-transaction-amount)
* [OWASP A09: Security Logging and Monitoring Failures](#owasp-a09-security-logging-and-monitoring-failures)
    - [A09-01: No Logging](#a09-01-no-logging)
* [OWASP A10: Server Side Request Forgery](#owasp-a10-server-side-request-forgery)
* [B01: Miscellaneous](#b01-miscellaneous)
    - [B01-01: Sort code generation denial of service vulnerability](#b01-01-sort-code-generation-denial-of-service-vulnerability)
    - [B01-02: Secrets shouldn't be stored in code](#b01-02-secrets-shouldn't-be-stored-in-code)
    - [B01-03: Cross-site request forgery (CSRF)](#b01-03-cross-site-request-forgery-csrf)
* [B02: Non-security Critical Issues](#b02-non-security-critical-issues)
    - [B02-01: Bad or No Input Validation (General Cases)](#b02-01-bad-or-no-input-validation-general-cases)
    - [B02-02: Admin permissions are assigned based on a fixed username instead of role](#b02-02-admin-permissions-are-assigned-based-on-a-fixed-username-instead-of-role)


## [OWASP A01: Broken Access Control](https://owasp.org/Top10/A01_2021-Broken_Access_Control/)
Access control enforces policy such that users cannot act outside of their intended permissions. Failures typically lead to unauthorized information disclosure, modification, or destruction of all data or performing a business function outside the user's limits.

### A01-01: Unauthorised users are allowed to visit secure pages
The `@add_to_navbar` decorator function is used to perform basic checks and not show logged in user only pages to anonymous users. However, slightly deceptively, this doesn't actually prevent a user who isn't signed in from accessing these pages!

#### [Solution](https://flask-login.readthedocs.io/en/latest/#protecting-views)
You should throw an error if the user tries to access a page they're not supposed to. This could be a 403 forbidden HTTP response. Flask-Login has the `@login_required` decorator which can be added to view functions to handle this for you.
### A01-02: No access control/owner check on account page
The account/transactions page does not perform any check that the user actually owns the account specified in the URL. This means that anyone can enter a sort code and account number and see the transaction history, or even worse use a script to enumerate all bank accounts on the system.

#### Solution
In the account page view, verify that the account belongs to the currently logged in user before returning any account details. Throw some error such as HTTP 403 Forbidden if it does not.
### A01-03: No access control on the admin page
[![XKCD 1200: "Authorization"](https://imgs.xkcd.com/comics/authorization.png)](https://xkcd.com/1200/)
> *Before you say anything, no, I know not to leave my computer sitting out logged in to all my accounts. I have it set up so after a few minutes of inactivity it automatically switches to my brother's.*

While it does not show in the navbar unless your username is admin, the admin page is accessible by any user. This page allows anyone to change a customer's credit score, which shouldn't be public!

#### Solution
In the admin page view, verify that the user is an admin in some way before returning the page. The exact way you do this is up to you, although we tried to suggest you just take the naive approach of checking if the username is admin. Throw some error such as HTTP 403 Forbidden otherwise.

## [OWASP A02: Cryptographic Failures](https://owasp.org/Top10/A02_2021-Cryptographic_Failures/)
Cryptography is used to secure communications or data at rest against adversarial behaviour. Cryptography failures can be caused by bad implementation, but also by bad choice of cipher algorithm in the first place.

### [A02-01: Unsuitable use of ROT-13 "encryption"](https://en.wikipedia.org/wiki/ROT13)
[![XKCD 538: "Security"](https://imgs.xkcd.com/comics/security.png)](https://xkcd.com/538/)
> *Actual actual reality: nobody cares about his secrets.  (Also, I would be hard-pressed to find that wrench for $5.)*

ROT-13 is a simple substitution cipher. It doesn't make use of any key and the plaintext can be easily recovered, even by hand.

#### Examples
*In [app.py](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py), line [122](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py#L122):*
```python
    if password_row is not None and password_row[0] == encode(request.form['password'], 'rot_13'):
```
*In [app.py](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py), lines [178-180](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py#L178-L180):*
```python
    # encrypt the password with rot-13 cryptography
    cursor.execute("insert into users (username, password, fullname) values (\"" + str(username) + "\", \""
                   + encode(str(password), 'rot_13') + "\", \"" + str(fullname) + "\")")
```
#### [Solution](https://www.youtube.com/watch?v=yoMOAIzBSpY)
While a better cipher could have been used, the proper solution is to use a robust hashing algorithm (such as bcrypt) to transform the passwords before storing instead. Hashing is a one way operation designed to make it easy to compare two passwords together, without being able to derive the plaintext from the stored hash itself. Best practice is to also use a salt - a unique piece of data (stored alongside the hash), added to the plaintext before hashing to prevent comparing passwords against pre-computed (or leaked) hashes, in so-called "rainbow table" attacks.
### [A02-02: Random number generation is not secure](https://en.wikipedia.org/wiki/Random_number_generation#%22True%22_vs._pseudo-random_numbers)
[![XKCD 2626: "d65536"](https://imgs.xkcd.com/comics/d65536.png)](https://xkcd.com/2626/)
> *They're robust against quantum attacks because it's hard to make a quantum system that large.*

A random number generator is used to generate bank account numbers. However, this uses a PRNG, which generates a reproducible series of numbers given some initial starting value (seed). Therefore, an adversary could find this seed and enumerate all bank account numbers.

#### Examples
*In [app.py](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py), line [7](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py#L7):*
```python
import random
```
*In [app.py](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py), lines [211-218](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py#L211-L218):*
```python
        sortnum1 = random.randrange(0, 100)
        sortnum2 = random.randrange(0, 100)

        # Creates the sort code in the correct format
        sort = "06-" + str(sortnum1).zfill(2) + "-" + str(sortnum2).zfill(2)

        # Generates a number for the account number
        accnum = random.randrange(0, 100000000)
```
#### [Solution](https://docs.python.org/3/library/secrets.html)
[![XKCD 221: "Random Number"](https://imgs.xkcd.com/comics/random_number.png)](https://xkcd.com/221/)
> *RFC 1149.5 specifies 4 as the standard IEEE-vetted random number.*

Use a cryptographically secure random number generator, such as Python's 'secrets' library.

## [OWASP A03: Injection](https://owasp.org/Top10/A03_2021-Injection/)
Code injection is caused by untrusted, unsanitized input being processed as exectuable code. This should be prevented by sanitizing input, thereby removing any characters which could cause the machine to begin processing the input as code.

### [A03-01: SQL Injection](https://www.w3schools.com/sql/sql_injection.asp)
[![XKCD 327: "Exploits of a Mom"](https://imgs.xkcd.com/comics/exploits_of_a_mom.png)](https://xkcd.com/327/)
> *Her daughter is named Help I'm trapped in a driver's license factory.*

The web app did not sanitise input before adding into SQL statements. This means maliciously crafted input from an attacker could be treated as direct SQL code, which would be executed on the database.

#### Examples
*In [app.py](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py), line [28](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py#L28):*
```python
    cursor.execute("select * from users where username = \"" + str(username) + "\"")
```
*In [app.py](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py), line [46](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py#L46):*
```python
    cursor.execute("select * from users where username = \"" + str(username) + "\"")
```
*In [app.py](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py), line [117](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py#L117):*
```python
    cursor.execute("select password from users where username = \"" + str(username) + "\"")
```
*In [app.py](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py), line [161](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py#L161):*
```python
    cursor.execute("select * from users where username = \"" + str(username) + "\"")
```
*In [app.py](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py), lines [179-180](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py#L179-L180):*
```python
    cursor.execute("insert into users (username, password, fullname) values (\"" + str(username) + "\", \""
                   + encode(str(password), 'rot_13') + "\", \"" + str(fullname) + "\")")
```
*In [app.py](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py), lines [227-228](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py#L227-L228):*
```python
        cursor.execute("select * from bank_accounts where sort_code = \"" + sort + "\" or account_number = \"" + acc +
                       "\"")
```
*In [app.py](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py), lines [244-245](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py#L244-L245):*
```python
    cursor.execute("insert into bank_accounts (username, sort_code, account_number, account_name) values (\""
                   + str(username) + "\", \"" + str(sort) + "\", \"" + str(acc) + "\", \"" + str(account) + "\")")
```
*In [app.py](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py), lines [274-275](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py#L274-L275):*
```python
    cursor.execute("select * from bank_accounts where sort_code = \"" + sort + "\" and account_number = \"" + acc +
                   "\"")
```
*In [app.py](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py), lines [292-293](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py#L292-L293):*
```python
    cursor.execute("select * from bank_accounts where username = \"" + username + "\" and sort_code = \"" + usersort +
                   "\" and account_number = \"" + useracc + "\"")
```
*In [app.py](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py), lines [306-308](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py#L306-L308):*
```python
    cursor.execute("insert into transactions (from_sort_code, from_account_number, to_sort_code, to_account_number, "
                   "amount) values (\"" + usersort + "\", \"" + useracc + "\", \"" + str(sort) + "\", \"" + str(acc) +
                   "\", \"" + str(amount) + "\")")
```
*In [app.py](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py), line [333](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py#L333):*
```python
    cursor.execute("select * from users where username = \"" + str(username) + "\"")
```
*In [app.py](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py), line [346](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py#L346):*
```python
    cursor.execute("update users set credit_score = " + str(score) + " where username = \"" + username + "\"")
```
*In [app.py](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py), lines [364-365](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py#L364-L365):*
```python
    cursor.execute(
        "select sort_code, account_number, account_name from bank_accounts where username = \"" + str(username) + "\"")
```
*In [app.py](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py), lines [383-389](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py#L383-L389):*
```python
            cursor.execute(
                f"SELECT"
                f"(SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE to_sort_code == '{sort_code}' AND to_account_number == '{account_number}')"
                f"-"
                f"(SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE from_sort_code == '{sort_code}' AND from_account_number == '{account_number}')"
                f"AS total;"
            )
```
*In [app.py](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py), line [412](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py#L412):*
```python
        cursor.execute("select credit_score from users where username = \"" + username + "\"").fetchone()[0])
```
*In [app.py](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py), lines [429-431](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py#L429-L431):*
```python
    cursor.execute(
        f"select * from transactions where (to_account_number == \"{account_number}\" and to_sort_code == \"{sort_code}\") "
        f"or (from_account_number == \"{account_number}\" and from_sort_code == \"{sort_code}\") order by timestamp desc;")
```
*In [app.py](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py), lines [433-439](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py#L433-L439):*
```python
    cursor.execute(
        f"SELECT"
        f"(SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE to_sort_code == '{sort_code}' AND to_account_number == '{account_number}')"
        f"-"
        f"(SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE from_sort_code == '{sort_code}' AND from_account_number == '{account_number}')"
        f"AS total;"
    )
```
#### [Solution](https://docs.python.org/3/library/sqlite3.html#sqlite3-placeholders)
Input needs to be sanitised in some way before being inserted into an SQL statement. While there are many ways to do this, one of the simplest is to use parameterised statements. This involves adding "placeholders" to your SQL statements, which your SQL library will then fill with your input data (which it automatically sanitises). Other methods such as using an ORM (like SQLAlchemy) use this method internally.

## [OWASP A04: Insecure Design](https://owasp.org/Top10/A04_2021-Insecure_Design/)
While most security failures can be put down to implementation error (typically a mistake made when writing code), some failures are so fundamental that they were made during the design of the system, and cannot be fixed by good code.

### [A04-01: No CAPTCHAs Used](https://en.wikipedia.org/wiki/CAPTCHA)
[![XKCD 1897: "Self Driving"](https://imgs.xkcd.com/comics/self_driving.png)](https://xkcd.com/1897/)
> *"Crowdsourced steering" doesn't sound quite as appealing as "self driving."*

The web app doesn't use CAPTCHAs to prevent bots from signing in, completing transactions or registering new accounts. CAPTCHAs require some form of evidence from the user that they are human, and prevent bots from completing actions that may be harmful to the business if automated or done en masse. This could be done to achieve denial of service, or simply using user credentials from database leaks to steal information or money.

#### [Solution](https://python.plainenglish.io/how-to-use-google-recaptcha-with-flask-dbd79d5ea193)
Use a CAPTCHA service, such as reCAPTCHA, on any form actions that could cause harm if done by a bot or en masse.
### [A04-02: No Password Strength Checks](https://en.wikipedia.org/wiki/Password_strength)
[![XKCD 936: "Password Strength"](https://imgs.xkcd.com/comics/password_strength.png)](https://xkcd.com/936/)
> *To anyone who understands information theory and security and is in an infuriating argument with someone who does not (possibly involving mixed case), I sincerely apologize.*

There are no password strength checks in the web app. Passwords need to be sufficiently complex (have enough bits of **entropy**) in order to resist brute-force attacks to some satisfactory level. There was no such protection in the web app, meaning the user would be permitted to choose a weak password that could be easily guessed.

#### [Solution](https://www.section.io/engineering-education/password-strength-checker-javascript/)
Check passwords match some minimum complexity requirement and reject them if they do not. You could also look the password up in a dictionary of common passwords, or even better a list of leaked passwords although this could freak the user out a little! If you decided to hash the password on client side and then again on the server side for whatever reason, you would need to perform this validation on the client side. However this is probably okay, since if someone crafted malicious requests to bypass the check they would only be purposely harming themselves - it depends on what your threat model could be.
### [A04-03: No Rate Limiting](https://en.wikipedia.org/wiki/Rate_limiting)
Rate limiting is used to prevent brute forcing or resources being depleted by unusually high traffic volumes. Without rate limiting, bots can brute force passwords by trying hundreds per second, or cause denial of service by purposely depleting server bandwidth or API quotas.

Limiting a user account to a certain number of password attempts before requiring additional verification is a form of rate limiting.

#### [Solution](https://www.section.io/engineering-education/implementing-rate-limiting-in-flask/)
Use a rate limiter in the web app (and possibly an external rate limiter/protection service like Cloudflare).
### [A04-04: Vulnerable to MITM attack](https://en.wikipedia.org/wiki/Man-in-the-middle_attack)
A machine-in-the-middle/man-in-the-middle attacks is when an adversary is able to silently intercept and relay communications between a client and a server, either passively listening in or actively altering data in transit. In the case of the web app, SSL/TLS (often refered to as part of HTTPS) is not used to encrypt web traffic. This means that an attacker could sniff the connection to retrieve things like passwords which are sent in plaintext.

#### [Solution](https://stackoverflow.com/questions/3715920/is-it-worth-hashing-passwords-on-the-client-side)
Use SSL on the web app, although this is difficult to achieve in the hackathon environment. You could also additionally hash the passwords on the client side before sending them and hashing again on the server, but this only gives slight protection from an attacker listening in being able to retrieve the plaintext password. If the attacker can get the client hash they would still be able to authenticate with that in the form of a replay attack. See the link for more information.

## [OWASP A05: Security Misconfiguration](https://owasp.org/Top10/A05_2021-Security_Misconfiguration/)
Security misconfigurations include things like default passwords being set and unnecessary features being left accidentally enabled.

### [A05-01: Flask secret key used is not secure](https://stackoverflow.com/questions/22463939/demystify-flask-app-secret-key)
Flask requires a secret key to be specified in the web app, which is used for cryptographic purposes. The provided default key is easy to guess or brute force, negating any security built into flask's cookie system.

#### Examples
*In [app.py](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py), line [12](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py#L12):*
```python
app.secret_key = 'hello'
```
#### [Solution](https://stackoverflow.com/questions/34902378/where-do-i-get-secret-key-for-flask)
This key should be a long and securely random string, preferably stored in a secrets file as opposed to raw in the source code itself.
### [A05-02: Flask debug mode is left enabled](https://www.educba.com/flask-debug-mode/)
Flask has a built in debug mode which, when enabled for your web app, allows you to get full error messages and tracebacks in your browser if your code throws an exception. It also gives you access to a Python console to run arbitary code in the context of the web app view. This is great for debugging, but is a huge security vulnerability as it allows remote code execution, along with revealing sensitive error information to users.

#### Examples
*In [app.py](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py), lines [472-473](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py#L472-L473):*
```python
    # run the app with debug mode on to show full error messages
    app.run(debug=True)
```
#### [Solution](https://arrayoverflow.com/question/how-to-turn-off-debug-mode-in-flask-app/606)
Disable debug mode when you call app.run().

## [OWASP A06: Vulnerable and Outdated Components](https://owasp.org/Top10/A06_2021-Vulnerable_and_Outdated_Components/)
Outdated components have the potential to introduce security vulnerabilities to a system. When a vulnerability is publicly found in a component, it will typically be patched by the vendor via an update and so promptly updating components is critical.

*There are no known vulnerabilities in this category.*

## [OWASP A07: Identification and Authentication Failures](https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/)
Whereas access control failures arise from allowing a known user access to something they shouldn't be able to, identification and authentication failures arise from mis-identifying the user in the first place.

### [A07-01: No multi-factor authentication available](https://en.wikipedia.org/wiki/Multi-factor_authentication)
[![XKCD 2522: "Two-Factor Security Key"](https://imgs.xkcd.com/comics/two_factor_security_key.png)](https://xkcd.com/2522/)
> *The bruises on my fingertips are my proof of work.*

The web app doesn't allow users to set up any kind of multi-factor authentication, such as a one-time password generated by an authenticator app. Such login "factors" (as they are known) can improve security by making it more difficult for adversaries to gain access to accounts if they only have one factor, such as a leaked password.

#### [Solution](https://www.section.io/engineering-education/implementing-totp-2fa-using-flask/)
[![XKCD 2543: "Never Told Anyone"](https://imgs.xkcd.com/comics/never_told_anyone.png)](https://xkcd.com/2543/)
> *Even if you said you were an employee of the website, if you asked for my password, I'd tell you.*

Use a library like `pyotp` to generate authenticator keys and validate a token generated by the user's authenticator app.

## [OWASP A08: Software and Data Integrity Failures](https://owasp.org/Top10/A08_2021-Software_and_Data_Integrity_Failures/)
Data integrity failures arise when data is erroneously trusted or it's integrity falsely assumed. A user could exploit the web app by modifying unsigned data that the server trusts in a web request.

### A08-01: Missing Validation for Lower Bound of Transaction Amount
There is no validation on the transaction amount given to ensure it is greater than 0. Therefore, a user could enter a negative transaction amount which would take money from the recipients account, effectively running the transaction backwards without permission, stealing money.

#### Solution
The input field on the web page should have a minimum value specified so the user cannot enter negative values, and the server should also validate this to ensure the client has not bypassed the field parameters by crafting a malicious request.

## [OWASP A09: Security Logging and Monitoring Failures](https://owasp.org/Top10/A09_2021-Security_Logging_and_Monitoring_Failures/)
If you don't know that something has gone wrong, you don't know that you need to fix it. Logging and monitoring (or "visibility", as it's often called) is important in keeping a system safe.

### [A09-01: No Logging](https://en.wikipedia.org/wiki/Logging_(software))
The web app does not keep logs for anything, including security critical events.

#### [Solution](https://flask.palletsprojects.com/en/2.2.x/logging/)
Use a logging library to keep logs. This could be just for security critical events (like incorrect logins), or it could include information level events like transactions where a "paper trail" could be useful to the business.

## [OWASP A10: Server Side Request Forgery](https://owasp.org/Top10/A10_2021-Server-Side_Request_Forgery_%28SSRF%29/)
Server Side Request Forgery causes the web server to make outgoing web requests to arbitary addresses specified by the user, which could be malicious.

*There are no known vulnerabilities in this category.*

## B01: Miscellaneous
Other security issues or vulnerabilities that don't precisely fit within any OWASP Top 10 category.

### B01-01: Sort code generation denial of service vulnerability
When creating a new account, the web app mistakenly enforces both the sort code and account number to be unique separately, whereas it should only require the combination of them to be unique. This means that rather than the system being able to handle 100 trillion different accounts it can instead only handle 10 thousand before it runs out of unique sort codes. Especially with no rate limiting, it would be trivial to create this many accounts and cause a denial of service as the web app would get stuck in an inifinte loop every time someone tries to open a new account.

#### Examples
*In [app.py](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py), lines [207-234](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py#L207-L234):*
```python
    # Flag for sort code/account number generation
    unique = False
    while not unique:
        # Generates two numbers for the sort code
        sortnum1 = random.randrange(0, 100)
        sortnum2 = random.randrange(0, 100)

        # Creates the sort code in the correct format
        sort = "06-" + str(sortnum1).zfill(2) + "-" + str(sortnum2).zfill(2)

        # Generates a number for the account number
        accnum = random.randrange(0, 100000000)

        # Creates the account number in the correct format
        acc = str(accnum).zfill(8)

        # Tries to retrieve a bank account from the database with the same sort code or account number
        connection = sqlite3.connect("falihax.db")
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute("select * from bank_accounts where sort_code = \"" + sort + "\" or account_number = \"" + acc +
                       "\"")
        row = cursor.fetchone()
        connection.close()

        # If no account is found then the numbers are unique
        if row is None:
            unique = True
```
#### Solution
Change the logic operator in the SQL statement from OR to AND, i.e., `sort_code = sort and account_number = acc`. This means the code will only mark a combination as already taken when an account exists with BOTH identifiers the same, rather than just one.

While this proper implementation is still hypothetically vulnerable to the denial of service issue, it would require 10 orders of magnitude more accounts to be created making this specific attack impractical - something else would probably fail first, such as the database disk becoming full.
### [B01-02: Secrets shouldn't be stored in code](https://en.wikipedia.org/wiki/Configuration_file)
Secrets are generally private keys or tokens used for cryptographic purposes within a web app, or to authenticate with some external service like an API. The web app stores the flask secret key in the code, which is insecure as anyone with access to read the code (which could be everyone in an open source project) would be able to sign cookies as though they were the server.

#### Examples
*In [app.py](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py), line [12](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py#L12):*
```python
app.secret_key = 'hello'
```
#### [Solution](https://medium.com/black-tech-diva/hide-your-api-keys-7635e181a06c)
Use some form of secrets storage or management tool, such as a configuration file. You can keep the configuration file out of your code repository and distribute it separately through some pre-existing, secure channel.
### [B01-03: Cross-site request forgery (CSRF)](https://en.wikipedia.org/wiki/Cross-site_request_forgery)
Cross-site request forgery refers to a third-party web page forging requests to some other web page, often taking advantage of things like the user being logged in on the site to perform unauthorised privileged actions. For example, the page to perform a transaction simply takes account details and an amount - there is nothing stopping an external website (while being used in the users browser) from making a fraudulent request to the web app and making a transaction without permission.

#### [Solution](https://testdriven.io/blog/csrf-flask/)
Send a CSRF token to the client with each page that includes a form. Validate the token on the server when the form is submitted and reject any submissions without a valid token. The `flask-wtf` library has built in CSRF functionality you can use.

## B02: Non-security Critical Issues
Issues or potential improvements that are not security critical, but bonus marks were awarded for fixing them anyway.

### B02-01: Bad or No Input Validation (General Cases)
There is generally no validation performed on input. While this can lead to general errors, bad user experience and even security vulnerabilities such as injection or data integrity failures, in itself it is not always security critical.

#### [Solution](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
Input validation will be different in each case, but in general works by declaring a series of constraints that input must meet to be accepted. 

Common contraints include:
- Data must be of a certain type (i.e., numeric/integer/float/string/file)
- Data must be within a certain range (i.e., minimum and maximum for numeric data)
- Data must not exceed a specified length

Input can either be transformed (i.e, numeric string converted to an integer) or more often rejected if it does not meet the validation constraints. Best practice is to validate on **both** the client and server side - client side validation makes it easier to present error information in the UI and reduces load on the server, whereas server side validation reliably prevents the invalid input from reaching business logic. Remember - you cannot trust the client side!
### B02-02: Admin permissions are assigned based on a fixed username instead of role
The limited admin permissions that exist are (at least supposed to be) assigned based on if the user's username is `admin`. This isn't a great solution, because what if there are multiple admin users? What if you forget to register the username admin, and someone else registers it first? What if your code forgets to apply the unique usernames constraint, and multiple people take the username `admin`? This isn't the best approach.

#### Examples
*In [app.py](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py), line [318](https://github.com/CyberSoc-Newcastle/owasp-falihax/blob/8afa29f877dca468be95bc2ef8e0bda6ce625586/app.py#L318):*
```python
@add_to_navbar("Admin", condition=lambda: current_user.is_authenticated and current_user.id == "admin")
```
#### Solution
One approach to take would be to create an admin "role" which can be assigned to users at will. This could take the form of an additional boolean database column to mark an account as an admin or not, among other ways.
