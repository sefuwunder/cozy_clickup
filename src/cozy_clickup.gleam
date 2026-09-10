//// Cozy ClickUp: read tasks from a JSON file and display them in a
//// cozy 8-bit SDL window.
////
//// The tasks file is written by the `clickup` skill's fetch helper
//// (which holds the API token), or you can hand-write one — see
//// `tasks.sample.json`. Then just `gleam run`.

import gleam/dynamic/decode
import gleam/io
import gleam/json
import gleam/list
import gleam/result
import gleam/string
import simplifile

/// A single task, already normalised to plain strings.
pub type Task {
  Task(name: String, status: String, priority: String, due: String)
}

fn task_decoder() -> decode.Decoder(Task) {
  use name <- decode.field("name", decode.string)
  use status <- decode.field("status", decode.string)
  use priority <- decode.field("priority", decode.string)
  use due <- decode.field("due", decode.string)
  decode.success(Task(name:, status:, priority:, due:))
}

fn tasks_decoder() -> decode.Decoder(List(Task)) {
  use tasks <- decode.field("tasks", decode.list(task_decoder()))
  decode.success(tasks)
}

fn parse_tasks(raw: String) -> Result(List(Task), String) {
  case json.parse(from: raw, using: tasks_decoder()) {
    Ok(tasks) -> Ok(tasks)
    Error(_) -> Error("Could not parse tasks.json — see tasks.sample.json")
  }
}

fn task_to_json(task: Task) -> json.Json {
  json.object([
    #("name", json.string(task.name)),
    #("status", json.string(task.status)),
    #("priority", json.string(task.priority)),
    #("due", json.string(task.due)),
  ])
}

pub fn main() -> Nil {
  let raw =
    simplifile.read("tasks.json")
    |> result.map_error(fn(_) { "tasks.json not found in " <> cwd() })
  case raw {
    Error(msg) -> io.println_error(msg)
    Ok(contents) -> {
      case parse_tasks(contents) {
        Error(msg) -> io.println_error(msg)
        Ok(tasks) -> {
          let shown = list.take(tasks, 12)
          io.println(
            "Lighting the lantern for "
            <> string.inspect(list.length(shown))
            <> " tasks…",
          )
          let render =
            json.object([
              #("title", json.string("TODAY'S QUESTS")),
              #("tasks", json.array(shown, task_to_json)),
            ])
            |> json.to_string
          let assert Ok(_) = simplifile.write("render.json", render)
          show("render.json")
        }
      }
    }
  }
}

fn cwd() -> String {
  get_cwd()
}

@external(erlang, "renderer_ffi", "get_cwd")
fn get_cwd() -> String

/// Open the cozy SDL window and block until it is closed.
@external(erlang, "renderer_ffi", "show")
fn show(path: String) -> Nil
