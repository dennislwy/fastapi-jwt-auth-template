# TODO List
## General
- [x] add code coverage to SonarQube
- [x] add SonarQube quality gate & code coverage score badge at README.md
- [x] add pylint & pytest Github workflows

## Auth
- [x] when login, allow "Remember me"
    - [x] No remember me, access token expiry in `15mins`, refresh token expiry in `1 hour`
    - [x] Remember me, access token expiry in `1 day`, refresh token expiry in `2 weeks`
    - [x] remember me info should store in session cache
- [x] Token revocation
    - [x] when user logged out, session will be revoked. Tokens of same session will denied access.
    - [x] active session info will be store in cache & database
        - session cache
            - key: `{user_id}{session_id}`, value: `SessionInfo`
            - expiry same as the recent refresh token
    - [x] valid tokens (whitelist tokens) will be store in cache
        - active token cache
            - key: `{token_id}`, value: `{sibling_token_id}`
            - expiry same as the token
- [x] Token replay attack prevention
    - when user refreshes tokens, old tokens (access & refresh token) will be revoked. Refresh token are for single use only
- [x] Token reuse attack prevention
    - As security measures, session will be revoke if revoked token was reused

## Login
- [x] `/login`, get JWT tokens
- [x] `/logout`, revoke session
- [x] `/refresh`, refresh JWT tokens
- [ ] Password management
    - [ ] `/change-password`
    - [ ] `/forgot-password`, send password reset magic link to user email
    - [ ] `/reset-password`, reset password

## User
- [ ] register new user
- [ ] invite new user (by sending invitation email with link, link will expire in 7 days)
- [ ] verify new user (by sending email to click a magic link or enter OTP, will expire in X hours)

## Session Tracking
- [ ] user able to view all active session (like GitHub)
    - [x] session_id
    - [x] user_id
    - [x] last_active
    - [x] last_user_agent
    - [x] last_ip_address
    - [x] exp (session expiration time)
    - last_location
    - login_time
    - login_user_agent
    - login_ip_address
    - login_location
- [ ] user can revoke selective session(s) or all sessions

## Two-factor Authentication
- [ ] Enroll 2FA via OTP app
- [ ] Enroll 2FA & send OTP via email
- [ ] Enroll 2FA & send OTP via SMS

## Caching
- [x] In-memory
- [ ] Redis
- [ ] Memcached

## API Protection
- [ ] Rate limiting
- [ ] CORS
- [ ] XSS attacks
- [ ] CSRF attacks

## Docker

## Tests
- [ ] Unit Tests

# References
