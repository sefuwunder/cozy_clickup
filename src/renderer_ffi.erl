%% FFI for cozy_clickup: launch the SDL renderer and wait for it.
-module(renderer_ffi).
-export([show/1, get_cwd/0]).

get_cwd() ->
  {ok, Dir} = file:get_cwd(),
  unicode:characters_to_binary(Dir).

%% Spawn `python3 renderer/cozy.py <path>` and block until the window
%% closes. Stdout/stderr are drained so a chatty renderer can't block.
show(Path) when is_binary(Path) ->
  show(binary_to_list(Path));
show(Path) ->
  Port = open_port({spawn, "python3 renderer/cozy.py " ++ Path},
                   [binary, exit_status, stderr_to_stdout, hide]),
  wait(Port).

wait(Port) ->
  receive
    {Port, {exit_status, 0}} -> nil;
    {Port, {exit_status, Code}} -> erlang:error({renderer_failed, Code});
    {Port, {data, _Data}} -> wait(Port)
  end.
