# app.add_middleware(KBaseAuth, some_attribute="some_attribute_here_if_needed")

# from fastapi.exception_handlers import (
#     http_exception_handler,
#     request_validation_exception_handler,
# )

# async def authenticated(request: Request, call_next):
#     settings = get_settings()
#
#     try:
#         if request.url.path not in unauthenticated_endpoints:
#             valid_user(request, auth_url=settings.auth_url, admin_role=settings.admin_role)
#         response = await call_next(request)
#         return response
#     except HTTPException as e:
#         return JSONResponse({"detail": e.detail}, status_code=e.status_code)
#     except Exception as e:
#         error_message = traceback.format_exc()
#
#         return JSONResponse({"detail": str(e), "exception": error_message}, status_code=500)
#
#         # return JSONResponse({"detail": f"Authentication failed {dir(e)}", }, status_code=500)


# unauthenticated_endpoints = ["/status", "/docs", "/openapi.json", "/redoc"]


# @app.middleware("http")
# async def authenticated(request: Request, call_next):
#     settings = get_settings()
#
#     try:
#         if request.url.path not in unauthenticated_endpoints:
#             valid_user(request, auth_url=settings.auth_url, admin_role=settings.admin_role)
#         response = await call_next(request)
#         return response
#     except HTTPException as e:
#         return JSONResponse({"detail": e.detail}, status_code=e.status_code)
#     except Exception as e:
#         error_message = traceback.format_exc()
#
#         return JSONResponse({"detail": str(e), "exception": error_message}, status_code=500)
#
#         # return JSONResponse({"detail": f"Authentication failed {dir(e)}", }, status_code=500)
