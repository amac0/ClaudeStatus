You are an excellent software developer. You write clean and efficient code. I am your colleague who is also working on the project. When you have questions you ask me and I can help you get things done.

We are writing a python script to parse a jsonl file. Use @src/ for any libraries you want to write, and @tests/ for tests. There is an example jsonl file in @example.jsonl that you can use for testing. We are writing a status display based on the file and the git status of the project. We will be displaying three things: (a) the last user prompt from the jsonl file; (b) the last git commit status message; (c) any current todo list in the jsonl file and its status. By default, the jsonl file should be in ~/.claude/projects/{cwd based foldername}/{most recent .jsonl file}. The {cwd based foldername} should be a folder name based on the current working directory. For example: /var/home/a/Code/ClaudeStatus would be "var-home-a-Code-ClaudeStatus".

In the @example.jsonl you will find that the last user prompt was "Do not do anything right now, this is a test." You will also find a recent ToDo list from another user prompt. It created with this jsonl line:
{"parentUuid":"437c8c45-1b28-4bee-bb07-0fa95b8b194d","isSidechain":false,"userType":"external","cwd":"/var/home/a/Code/ClaudeStatus","sessionId":"2fc9b73b-2bd2-497c-a77b-3a272bf84e1f","version":"1.0.31","message":{"id":"msg_01MnJW2PpHxvCC9u6yFFJXVu","type":"message","role":"assistant","model":"claude-sonnet-4-20250514","content":[{"type":"tool_use","id":"toolu_01YCLHB2LxiwM6zyCn57MsAY","name":"TodoWrite","input":{"todos":[{"id":"1","content":"Explore codebase structure and identify key files","status":"in_progress","priority":"high"},{"id":"2","content":"Check for existing configuration files (package.json, pyproject.toml, etc.)","status":"pending","priority":"high"},{"id":"3","content":"Analyze code architecture and patterns","status":"pending","priority":"medium"},{"id":"4","content":"Create comprehensive CLAUDE.md file","status":"pending","priority":"high"}]}}],"stop_reason":null,"stop_sequence":null,"usage":{"input_tokens":3,"cache_creation_input_tokens":14938,"cache_read_input_tokens":0,"output_tokens":1,"service_tier":"standard"}},"requestId":"req_011CQcY6LbvGmLj4LTJwXauH","type":"assistant","uuid":"4a0fec7b-296a-45bb-a330-fae7cd46213d","timestamp":"2025-06-29T12:47:10.012Z"}

 And finally updated with all tasks done with this:
 {"parentUuid":"a47d58a5-7b00-4759-b2df-bc39cd7fafce","isSidechain":false,"userType":"external","cwd":"/var/home/a/Code/ClaudeStatus","sessionId":"2fc9b73b-2bd2-497c-a77b-3a272bf84e1f","version":"1.0.31","type":"user","message":{"role":"user","content":[{"tool_use_id":"toolu_01A1hjGArjYHR77NjaJUi57H","type":"tool_result","content":"Todos have been modified successfully. Ensure that you continue to use the todo list to track your progress. Please proceed with the current tasks if applicable"}]},"uuid":"f67a3a7c-38a0-4b76-a745-978628616f25","timestamp":"2025-06-29T12:48:17.113Z","toolUseResult":{"oldTodos":[{"content":"Explore codebase structure and identify key files","status":"completed","priority":"high","id":"1"},{"content":"Check for existing configuration files (package.json, pyproject.toml, etc.)","status":"completed","priority":"high","id":"2"},{"content":"Analyze code architecture and patterns","status":"completed","priority":"medium","id":"3"},{"content":"Create comprehensive CLAUDE.md file","status":"in_progress","priority":"high","id":"4"}],"newTodos":[{"content":"Explore codebase structure and identify key files","status":"completed","priority":"high","id":"1"},{"content":"Check for existing configuration files (package.json, pyproject.toml, etc.)","status":"completed","priority":"high","id":"2"},{"content":"Create comprehensive CLAUDE.md file","status":"completed","priority":"high","id":"4"},{"content":"Analyze code architecture and patterns","status":"completed","priority":"medium","id":"3"}]}}


The script should have a few command-line flags: "file" which changes the location of the projects jsonl file (use that for testing with @example.jsonl); "one-line" which truncates the status to be displayed on one terminal line (varying based on the terminal width); and "update" which will run the script and keep it displaying the current status over time until exited.

Take a moment now to come up with a plan to implement this script. Implement test driven development. That means FIRST write a test that the script needs to pass based on the functional requirements above and then write the code so that the test passes. To develop your plan, iterate based on the smallest reasonable chunks of testing/coding and commit each step of the way. Plan your implementation steps in order to get to runnable and useful code ASAP so that I can also see the status. Use your todo list tool to be able to track what you have done and what is still left to do. If you have questions about implementation or testing, please ask me.

Extra scratch space:
Make the following changes to the output.
"Last User Prompt:" -> "Current Prompt ({minutes} minutes ago):"
"Git Status: Last commit:" -> "Last Commit ({minutes} minutes ago)"
"Todo Status:" -> "Last Todos ({minutes} minutes ago)"

Make the following changes to the output.
"Current Prompt (1 minutes ago): -> "Prompt (1 minutes ago):"
"Last Commit (1 minutes ago):" -> "Commit (1 minutes ago):"
"Last Todos:" -> "Todos:"

Also, if there are no todos found, please just omit the todos entirely (don't display "no todos"). In both the regular and two-line display.

The two-line display needs to ensure that none of its output from the prompt,
todos or git have new-lines. Those should be converted to spaces.
