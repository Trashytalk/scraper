# JWT Security

The backend uses JSON Web Tokens for authentication. The following environment variables configure token handling:

- `JWT_SECRET` – signing key used to create and verify tokens (required).
- `JWT_ALGORITHM` – algorithm for signing, typically `HS256`.
- `JWT_AUDIENCE` and `JWT_ISSUER` – optional claims validated on each request.
- `JWT_EXP_DELTA` – token lifetime in seconds; defaults to 3600.

Generate a token after login and send it in the `Authorization` header using the `Bearer` scheme. Always keep the secret value private and enable HTTPS in production to protect credentials.
