# 全流程自动化执行报告

**执行时间**: 2025-07-01 08:43:02
**执行状态**: ❌ 失败

## 📊 执行统计
- 总步骤数: 44
- 成功步骤: 13
- 失败步骤: 10
- 成功率: 29.5%

## 📋 执行步骤详情
- ⏳ **检查pip版本** (RUNNING) - 2025-07-01 08:41:06
- ✅ **检查pip版本** (SUCCESS) - 2025-07-01 08:41:06
  - 执行成功
- ⏳ **升级pip** (RUNNING) - 2025-07-01 08:41:06
- ✅ **升级pip** (SUCCESS) - 2025-07-01 08:41:07
  - 执行成功
- ⏳ **安装安全工具** (RUNNING) - 2025-07-01 08:41:07
- ✅ **安装安全工具** (SUCCESS) - 2025-07-01 08:41:08
  - 执行成功
- ⏳ **升级项目依赖** (RUNNING) - 2025-07-01 08:41:08
- ✅ **升级项目依赖** (SUCCESS) - 2025-07-01 08:41:14
  - 执行成功
- ⏳ **运行安全修复脚本** (RUNNING) - 2025-07-01 08:41:14
- ✅ **运行安全修复脚本** (SUCCESS) - 2025-07-01 08:41:15
  - 执行成功
- ⏳ **运行安全扫描** (RUNNING) - 2025-07-01 08:41:15
- ❌ **运行安全扫描** (ERROR) - 2025-07-01 08:41:18
  - 执行失败: [main]	INFO	profile include tests: None
[main]	INFO	profile exclude tests: None
[main]	INFO	cli include tests: None
[main]	INFO	cli exclude tests: None
[json]	INFO	JSON output written to file: security_scan_final.json

- ⏳ **运行代码分析** (RUNNING) - 2025-07-01 08:41:18
- ✅ **运行代码分析** (SUCCESS) - 2025-07-01 08:41:19
  - 执行成功
- ⏳ **运行代码优化** (RUNNING) - 2025-07-01 08:41:19
- ✅ **运行代码优化** (SUCCESS) - 2025-07-01 08:41:19
  - 执行成功
- ⏳ **运行项目清理** (RUNNING) - 2025-07-01 08:41:19
- ❌ **运行项目清理** (ERROR) - 2025-07-01 08:41:20
  - 执行失败:   File "/Users/ON-MY-WAY/创业/GamePlayer-Raspberry/tools/dev/project_cleaner.py", line 238
    """TODO: Add docstring"""
    ^
SyntaxError: invalid syntax

- ⏳ **运行核心功能测试** (RUNNING) - 2025-07-01 08:41:20
- ❌ **运行核心功能测试** (ERROR) - 2025-07-01 08:41:25
  - 执行失败: 
- ⏳ **运行单元测试** (RUNNING) - 2025-07-01 08:41:25
- ❌ **运行单元测试** (ERROR) - 2025-07-01 08:41:26
  - 执行失败: 
- ⏳ **运行快速功能测试** (RUNNING) - 2025-07-01 08:41:26
- ✅ **运行快速功能测试** (SUCCESS) - 2025-07-01 08:41:27
  - 执行成功
- ❌ **步骤失败: 测试执行** (ERROR) - 2025-07-01 08:41:27
  - 步骤执行失败，但继续执行后续步骤
- ⏳ **检查模拟器集成** (RUNNING) - 2025-07-01 08:41:27
- ❌ **检查模拟器集成** (ERROR) - 2025-07-01 08:42:58
  - 执行失败: Traceback (most recent call last):
  File "/Users/ON-MY-WAY/Library/Python/3.9/lib/python/site-packages/urllib3/connectionpool.py", line 716, in urlopen
    httplib_response = self._make_request(
  File "/Users/ON-MY-WAY/Library/Python/3.9/lib/python/site-packages/urllib3/connectionpool.py", line 404, in _make_request
    self._validate_conn(conn)
  File "/Users/ON-MY-WAY/Library/Python/3.9/lib/python/site-packages/urllib3/connectionpool.py", line 1061, in _validate_conn
    conn.connect()
  File "/Users/ON-MY-WAY/Library/Python/3.9/lib/python/site-packages/urllib3/connection.py", line 419, in connect
    self.sock = ssl_wrap_socket(
  File "/Users/ON-MY-WAY/Library/Python/3.9/lib/python/site-packages/urllib3/util/ssl_.py", line 458, in ssl_wrap_socket
    ssl_sock = _ssl_wrap_socket_impl(
  File "/Users/ON-MY-WAY/Library/Python/3.9/lib/python/site-packages/urllib3/util/ssl_.py", line 502, in _ssl_wrap_socket_impl
    return ssl_context.wrap_socket(sock, server_hostname=server_hostname)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/ssl.py", line 500, in wrap_socket
    return self.sslsocket_class._create(
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/ssl.py", line 1040, in _create
    self.do_handshake()
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/ssl.py", line 1309, in do_handshake
    self._sslobj.do_handshake()
ssl.SSLEOFError: EOF occurred in violation of protocol (_ssl.c:1129)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/Users/ON-MY-WAY/Library/Python/3.9/lib/python/site-packages/requests/adapters.py", line 667, in send
    resp = conn.urlopen(
  File "/Users/ON-MY-WAY/Library/Python/3.9/lib/python/site-packages/urllib3/connectionpool.py", line 802, in urlopen
    retries = retries.increment(
  File "/Users/ON-MY-WAY/Library/Python/3.9/lib/python/site-packages/urllib3/util/retry.py", line 594, in increment
    raise MaxRetryError(_pool, url, error or ResponseError(cause))
urllib3.exceptions.MaxRetryError: HTTPSConnectionPool(host='github.com', port=443): Max retries exceeded with url: /SourMesen/Mesen/releases/download/0.9.9/Mesen.0.9.9.zip (Caused by SSLError(SSLEOFError(8, 'EOF occurred in violation of protocol (_ssl.c:1129)')))

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/Users/ON-MY-WAY/创业/GamePlayer-Raspberry/tools/dev/auto_install_top_nes_emulators.py", line 187, in <module>
    install_mesen()
  File "/Users/ON-MY-WAY/创业/GamePlayer-Raspberry/tools/dev/auto_install_top_nes_emulators.py", line 99, in install_mesen
    download_file(url, out_path)
  File "/Users/ON-MY-WAY/创业/GamePlayer-Raspberry/tools/dev/auto_install_top_nes_emulators.py", line 42, in download_file
    r = requests.get(url, stream=True)
  File "/Users/ON-MY-WAY/Library/Python/3.9/lib/python/site-packages/requests/api.py", line 73, in get
    return request("get", url, params=params, **kwargs)
  File "/Users/ON-MY-WAY/Library/Python/3.9/lib/python/site-packages/requests/api.py", line 59, in request
    return session.request(method=method, url=url, **kwargs)
  File "/Users/ON-MY-WAY/Library/Python/3.9/lib/python/site-packages/requests/sessions.py", line 589, in request
    resp = self.send(prep, **send_kwargs)
  File "/Users/ON-MY-WAY/Library/Python/3.9/lib/python/site-packages/requests/sessions.py", line 703, in send
    r = adapter.send(request, **kwargs)
  File "/Users/ON-MY-WAY/Library/Python/3.9/lib/python/site-packages/requests/adapters.py", line 698, in send
    raise SSLError(e, request=request)
requests.exceptions.SSLError: HTTPSConnectionPool(host='github.com', port=443): Max retries exceeded with url: /SourMesen/Mesen/releases/download/0.9.9/Mesen.0.9.9.zip (Caused by SSLError(SSLEOFError(8, 'EOF occurred in violation of protocol (_ssl.c:1129)')))

- ⏳ **运行Docker模拟测试** (RUNNING) - 2025-07-01 08:42:58
- ❌ **运行Docker模拟测试** (ERROR) - 2025-07-01 08:42:58
  - 执行失败:   File "/Users/ON-MY-WAY/创业/GamePlayer-Raspberry/src/scripts/quick_docker_test.sh", line 14
    log_info() {
               ^
SyntaxError: invalid syntax

- ⏳ **运行游戏启动测试** (RUNNING) - 2025-07-01 08:42:58
- ❌ **运行游戏启动测试** (ERROR) - 2025-07-01 08:42:58
  - 执行失败: usage: run_nes_game.py [-h] [--emulator EMULATOR] [--list-emulators] [rom]
run_nes_game.py: error: unrecognized arguments: --test

- ❌ **步骤失败: 模拟器测试** (ERROR) - 2025-07-01 08:42:58
  - 步骤执行失败，但继续执行后续步骤
- ⏳ **生成项目状态报告** (RUNNING) - 2025-07-01 08:42:58
- ❌ **生成项目状态报告** (ERROR) - 2025-07-01 08:42:58
  - 执行失败:   File "/Users/ON-MY-WAY/创业/GamePlayer-Raspberry/src/scripts/cleanup_and_report.sh", line 14
    log_info() {
               ^
SyntaxError: invalid syntax

- ⏳ **更新文档** (RUNNING) - 2025-07-01 08:42:58
- ✅ **更新文档** (SUCCESS) - 2025-07-01 08:42:58
  - 执行成功
- ⏳ **检查Git状态** (RUNNING) - 2025-07-01 08:42:58
- ✅ **检查Git状态** (SUCCESS) - 2025-07-01 08:42:58
  - 执行成功
- ⏳ **添加所有更改** (RUNNING) - 2025-07-01 08:42:58
- ✅ **添加所有更改** (SUCCESS) - 2025-07-01 08:42:58
  - 执行成功
- ⏳ **提交更改** (RUNNING) - 2025-07-01 08:42:58
- ✅ **提交更改** (SUCCESS) - 2025-07-01 08:42:58
  - 执行成功
- ⏳ **推送到远程仓库** (RUNNING) - 2025-07-01 08:42:58
- ✅ **推送到远程仓库** (SUCCESS) - 2025-07-01 08:43:02
  - 执行成功

## ❌ 错误信息
- 运行安全扫描: 执行失败: [main]	INFO	profile include tests: None
[main]	INFO	profile exclude tests: None
[main]	INFO	cli include tests: None
[main]	INFO	cli exclude tests: None
[json]	INFO	JSON output written to file: security_scan_final.json

- 运行项目清理: 执行失败:   File "/Users/ON-MY-WAY/创业/GamePlayer-Raspberry/tools/dev/project_cleaner.py", line 238
    """TODO: Add docstring"""
    ^
SyntaxError: invalid syntax

- 运行核心功能测试: 执行失败: 
- 运行单元测试: 执行失败: 
- 检查模拟器集成: 执行失败: Traceback (most recent call last):
  File "/Users/ON-MY-WAY/Library/Python/3.9/lib/python/site-packages/urllib3/connectionpool.py", line 716, in urlopen
    httplib_response = self._make_request(
  File "/Users/ON-MY-WAY/Library/Python/3.9/lib/python/site-packages/urllib3/connectionpool.py", line 404, in _make_request
    self._validate_conn(conn)
  File "/Users/ON-MY-WAY/Library/Python/3.9/lib/python/site-packages/urllib3/connectionpool.py", line 1061, in _validate_conn
    conn.connect()
  File "/Users/ON-MY-WAY/Library/Python/3.9/lib/python/site-packages/urllib3/connection.py", line 419, in connect
    self.sock = ssl_wrap_socket(
  File "/Users/ON-MY-WAY/Library/Python/3.9/lib/python/site-packages/urllib3/util/ssl_.py", line 458, in ssl_wrap_socket
    ssl_sock = _ssl_wrap_socket_impl(
  File "/Users/ON-MY-WAY/Library/Python/3.9/lib/python/site-packages/urllib3/util/ssl_.py", line 502, in _ssl_wrap_socket_impl
    return ssl_context.wrap_socket(sock, server_hostname=server_hostname)
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/ssl.py", line 500, in wrap_socket
    return self.sslsocket_class._create(
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/ssl.py", line 1040, in _create
    self.do_handshake()
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/ssl.py", line 1309, in do_handshake
    self._sslobj.do_handshake()
ssl.SSLEOFError: EOF occurred in violation of protocol (_ssl.c:1129)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/Users/ON-MY-WAY/Library/Python/3.9/lib/python/site-packages/requests/adapters.py", line 667, in send
    resp = conn.urlopen(
  File "/Users/ON-MY-WAY/Library/Python/3.9/lib/python/site-packages/urllib3/connectionpool.py", line 802, in urlopen
    retries = retries.increment(
  File "/Users/ON-MY-WAY/Library/Python/3.9/lib/python/site-packages/urllib3/util/retry.py", line 594, in increment
    raise MaxRetryError(_pool, url, error or ResponseError(cause))
urllib3.exceptions.MaxRetryError: HTTPSConnectionPool(host='github.com', port=443): Max retries exceeded with url: /SourMesen/Mesen/releases/download/0.9.9/Mesen.0.9.9.zip (Caused by SSLError(SSLEOFError(8, 'EOF occurred in violation of protocol (_ssl.c:1129)')))

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/Users/ON-MY-WAY/创业/GamePlayer-Raspberry/tools/dev/auto_install_top_nes_emulators.py", line 187, in <module>
    install_mesen()
  File "/Users/ON-MY-WAY/创业/GamePlayer-Raspberry/tools/dev/auto_install_top_nes_emulators.py", line 99, in install_mesen
    download_file(url, out_path)
  File "/Users/ON-MY-WAY/创业/GamePlayer-Raspberry/tools/dev/auto_install_top_nes_emulators.py", line 42, in download_file
    r = requests.get(url, stream=True)
  File "/Users/ON-MY-WAY/Library/Python/3.9/lib/python/site-packages/requests/api.py", line 73, in get
    return request("get", url, params=params, **kwargs)
  File "/Users/ON-MY-WAY/Library/Python/3.9/lib/python/site-packages/requests/api.py", line 59, in request
    return session.request(method=method, url=url, **kwargs)
  File "/Users/ON-MY-WAY/Library/Python/3.9/lib/python/site-packages/requests/sessions.py", line 589, in request
    resp = self.send(prep, **send_kwargs)
  File "/Users/ON-MY-WAY/Library/Python/3.9/lib/python/site-packages/requests/sessions.py", line 703, in send
    r = adapter.send(request, **kwargs)
  File "/Users/ON-MY-WAY/Library/Python/3.9/lib/python/site-packages/requests/adapters.py", line 698, in send
    raise SSLError(e, request=request)
requests.exceptions.SSLError: HTTPSConnectionPool(host='github.com', port=443): Max retries exceeded with url: /SourMesen/Mesen/releases/download/0.9.9/Mesen.0.9.9.zip (Caused by SSLError(SSLEOFError(8, 'EOF occurred in violation of protocol (_ssl.c:1129)')))

- 运行Docker模拟测试: 执行失败:   File "/Users/ON-MY-WAY/创业/GamePlayer-Raspberry/src/scripts/quick_docker_test.sh", line 14
    log_info() {
               ^
SyntaxError: invalid syntax

- 运行游戏启动测试: 执行失败: usage: run_nes_game.py [-h] [--emulator EMULATOR] [--list-emulators] [rom]
run_nes_game.py: error: unrecognized arguments: --test

- 生成项目状态报告: 执行失败:   File "/Users/ON-MY-WAY/创业/GamePlayer-Raspberry/src/scripts/cleanup_and_report.sh", line 14
    log_info() {
               ^
SyntaxError: invalid syntax


## ⚠️ 警告信息
- 步骤 测试执行 执行失败
- 步骤 模拟器测试 执行失败

## 💡 建议
- 🔧 存在执行错误，请检查错误信息
- 🛠️ 修复错误后重新运行脚本