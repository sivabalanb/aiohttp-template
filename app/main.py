import asyncio
from aiohttp import web
from aiohttp.client_context import ClientSessionContext, create_client_session_context

from common import logger
from common import request_id

app = web.Application()
app['client_session'] = ClientSession()

async def index(request: web.Request):
    async with app['client_session']() as session:
        response = await session.get('https://www.example.com')
        return web.Response(text=response.text)

@app.get('/user', include_in_schema=False)
async def user(request: web.Request):
    user_id = request.match_info['user_id']
    return web.json_response({"user_id": user_id})

@app.exception(aiohttp.ClientError)
async def handle_client_error(request: web.Request, error: aiohttp.ClientError) -> web.Response:
    logger.error(f"Client error: {error}")
    return web.Response(status=400, text=error.__class__.__name__)

def create_client_session_context():
    return ClientSessionContext(app['client_session'])

@app.middleware('after_request')
async def log_request_id(request: web.Request, handler: web.RequestHandler, response: web.Response):
    request_id = request_id.get(request)
    logger.debug(f"Request ID: {request_id} - {response.status}")
    return response

@app.middleware('before_start_server')
async def setup_logging():
    logger.init()

@app.middleware('/')
async def check_credentials(request: web.Request, handler: web.RequestHandler):
    if not request.headers.get('Authorization'):
        return web.HTTPUnauthorized(text="Missing Authorization header")

    try:
        username, _, password = request.headers['Authorization'].split()
    except ValueError:
        return web.HTTPUnauthorized(text="Invalid Authorization header")

    if username != 'user' or password != 'password':
        return web.HTTPUnauthorized(text="Invalid username or password")

    await handler(request)

app.router.add_routes([
    web.get('/index', index),
    app.get('/user', user)
])

app.cleanup_ctx.append(create_client_session_context)

async def start_server():
    runner = web.AppRunner(app)
    await runner.start()
    site = runner.make_handler()
    server = await asyncio.start_server(site, '0.0.0.0', 8080)
    print('Server started at http://localhost:8080')
    try:
        await server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        await runner.cleanup()

if __name__ == '__main__':
    asyncio.run(start_server())
