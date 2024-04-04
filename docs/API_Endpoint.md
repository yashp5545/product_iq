# User

## User Registration


`POST /api/v1/auth/register`

```json
{
    "username": "swaro5or3p34700v111",
    "email": "s@g.c3495rv301171",
    "password": "1946",
    "product_exp":"Beginner",
    "name": "Swroop Dora"
}
```
Responce

```json
{
    "id": 8,
    "username": "swaro5or3p34700v111",
    "email": "s@g.c3495rv301171",
    "name": "Swroop Dora",
    "phone_number": "",
    "job_title": "",
    "company_or_institiution": "",
    "product_exp": "Beginner"
}
```

## User Login

`POST /api/v1/auth/login`

```json
{
    "email": "hello@gmail.com",
    "password": "password",
}
```

Responce

```json
{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo2LCJleHAiOjE3MTIwNTY1MTgsImlhdCI6MTcxMjA1NjQ4OH0.mfJ0cv6c_TAqsphzblN4cHGJuf1rX93o2fTpRVoWncw"
}
```

Cookies

```json
token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo2LCJleHAiOjE3MTIwNTY1MTgsImlhdCI6MTcxMjA1NjQ4OH0.mfJ0cv6c_TAqsphzblN4cHGJuf1rX93o2fTpRVoWncw; Path=/; HttpOnly; Secure; SameSite=None`
```

## User Logout

`POST /api/v1/auth/logout`

Responce

```json
{
    "message": "User logged out successfully"
}
```

## User Profile

`GET /api/v1/auth/user`

Headers

```json
{
    "Authorization": "Bearer token"
}
```

responce

```json
{
    "id": 6,
    "username": "hello",
    "email": "x"
}
```

## refresh token

`POST /api/v1/auth/refresh`

Cookies

```json
{
    "refressToken": "token"
}

Responce

```json
{
    "token": "eyJhbGci.."
}
```
