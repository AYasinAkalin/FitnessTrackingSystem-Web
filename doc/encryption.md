# Encryption tools

There are two hash functions we are using.

1. [Argon2](#argon2)
	- [Original repository - redirects to Github](https://github.com/P-H-C/phc-winner-argon2)
	- [Flash-Argon2 repository - redirects to Github](https://github.com/red-coracle/flask-argon2)
2. [SHA-2 (SHA-256)](#sha2)
	- [Passlib documentation](https://passlib.readthedocs.io/en/stable/lib/passlib.hash.sha256_crypt.html)

## Argon2

We are using Flask-Argon2 module to implement Argon2 hash function in our Python code.

## Installation

Install the extension with the following command:

```bash
$ sudo pip install flask-argon2
```

or use requirements.txt

```
$ sudo pip install -r requirements.txt
```

## Implementation

To use the extension simply import the class wrapper and pass the Flask app
object back to here. Do so like this:

    from flask import Flask
    from flask_argon2 import Argon2

    app = Flask(__name__)
    argon2 = Argon2(app)

---

Two primary methods are now exposed by way of the `argon2` object. These are: 

### Hash generating function

Generate **hash**, then push it to database.
`.generate_password_hash(str)` returns a *string*.

**Usage**:

```python
hash1 = argon2.generate_password_hash('text_to_be_encrypted')
```


### Hash checking function

Pull **hash** from database, check if it is the true hash. Proceed accordingly.
`.check_password_hash(str1, str2)` returns *boolean* value.

**Usage**:

```python
argon2.check_password_hash(hash1, 'entered_password')
```

---

## SHA2

We are using Passlib library to implement SHA256 hash function in our Python code.

## Installiation

Install the extension with the following command:

```bash
$ sudo pip install passlib
```

or use requirements.txt

```
$ sudo pip install -r requirements.txt
```

## Implementation

To start using SHA2/SHA256 encrytion we just need to import library to our python file.

```python
from passlib.hash import sha256_crypt
```

---

There are two basic functions we are going to use. These are: 

### Hash generating function
Generate **hash**, then push it to database.
`.generate_password_hash(str)` returns a *string* with an automatically created salt which is unique to hash.

**Usage**:

```python
hash2 = sha256_crypt.generate_password_hash('text_to_be_encrypted')
```

### Hash checking function

Pull **hash** from database, check if it is the true hash. Proceed accordingly.
`.check_password_hash(str1, str2)` returns *boolean* value.

**Usage**:

```python
sha256_crypt.verify('entered_password', hash2)
```