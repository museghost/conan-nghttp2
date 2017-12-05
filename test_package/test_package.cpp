// https://stackoverflow.com/a/35368387
#if defined(_MSC_VER)
#include <BaseTsd.h>
typedef SSIZE_T ssize_t;
#endif

#include <nghttp2/nghttp2.h>

#ifdef WITH_ASIO
#include <nghttp2/asio_http2_client.h>
#include <nghttp2/asio_http2_server.h>
#endif


int main()
{
    nghttp2_session_callbacks *callbacks;
    nghttp2_session_callbacks_new(&callbacks);
    nghttp2_session_callbacks_del(callbacks);

#ifdef WITH_ASIO
    nghttp2::asio_http2::server::http2 server;
#endif
}
