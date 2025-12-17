# CrewAI Features for AI Real Estate Agent

This steering file documents the 11 CrewAI features we will use in this project.

---

## 1. Flows

CrewAI Flows provide structured, event-driven workflow orchestration for combining multiple crews.

**Key Capabilities:**
- Combine different AI interaction patterns (crews, direct LLM calls, regular code)
- Build event-driven systems with decorators (@start, @listen)
- Maintain state across components using structured/unstructured state management
- Create complex execution paths with conditional branches and parallel processing
- Integrate seamlessly with external systems (databases, APIs, user interfaces)

**Our Usage:**
- We will have 3 different crews orchestrated through a single Flow
- Flow will manage the 5-phase workflow: Deep Discovery → Human Decision Gate → Intelligence Phase → Engagement Phase → Delivery Phase
- State will persist property records, approvals, and call results across phases

---

## 2. Sequential and Hierarchical Processes

CrewAI supports two process types for task execution within crews.

**Sequential Process:**
- Tasks execute one after another in linear progression
- Output of one task serves as context for the next
- Ideal for structured workflows with clear dependencies
- Default process type

**Hierarchical Process:**
- Manager agent coordinates the crew, delegating tasks and validating outcomes
- Requires `manager_llm` or `manager_agent` to be specified
- Manager allocates tasks based on agent capabilities
- Better for complex projects requiring dynamic task allocation and oversight

**Our Usage:**
- Sequential for Research Crew (scrape → extract → validate)
- Hierarchical for Voice AI Crew (manager coordinates Inspector/Negotiator agents)

---

## 3. Training

CrewAI Training enables interactive feedback loops to improve agent performance over time.

**How It Works:**
- During training runs, system records: initial_output, human_feedback, improved_output
- Data stored in `training_data.pkl` keyed by agent ID and iteration
- Agent automatically appends prior human feedback to prompts during training session
- Tasks must have `human_input=True` for training to work

**Recommendations:**
- Use models with at least 7B parameters for optimal training quality
- More powerful models provide higher quality feedback with better reasoning
- Smaller models may require more human intervention during training

**Our Usage:**
- Train Voice AI agents (Inspector, Negotiator) on conversation quality
- Train Research Agent on data extraction accuracy

---

## 4. Basic Memory System

CrewAI Memory enables agents to remember, reason, and learn from interactions.

**Memory Components:**
- **Short-Term Memory**: Temporary storage for immediate context using RAG (ChromaDB)
- **Long-Term Memory**: Persistent storage for learned patterns using SQLite3
- **Entity Memory**: Captures entities (people, places, concepts) using RAG
- **Contextual Memory**: Combines all memory types for coherent responses

**Benefits:**
- Adaptive Learning: Crews become more efficient over time
- Enhanced Personalization: Remember user preferences and historical interactions
- Improved Problem Solving: Draw on past learnings and contextual insights

**Storage Locations:**
- Windows: `C:\Users\{username}\AppData\Local\CrewAI\{project_name}\`
- Custom: Set `CREWAI_STORAGE_DIR` environment variable

**Our Usage:**
- Enable memory for background operations (retain context across call retries)
- Store property search history and user preferences
- Maintain entity memory for agents, properties, and contacts

---

## 5. Reasoning

Reasoning enables agents to plan and reflect before executing complex tasks.

**How It Works:**
1. Agent reflects on the task and creates a detailed plan
2. Evaluates whether it's ready to execute
3. Refines the plan until ready or max_reasoning_attempts reached
4. Injects the reasoning plan into task description before execution

**Configuration:**
- `reasoning=True` - Enable reasoning for the agent
- `max_reasoning_attempts` - Maximum attempts to refine plan (None for unlimited)

**Benefits:**
- Breaks down complex tasks into manageable steps
- Identifies potential challenges before starting
- Improves quality of complex decision-making

**Our Usage:**
- Enable for Negotiator AI (complex persuasion strategies)
- Enable for Location Analyzer (multi-factor proximity analysis)

---

## 6. Planning

Planning adds crew-level planning capability before task execution.

**How It Works:**
- When `planning=True`, before each crew iteration all data is sent to AgentPlanner
- AgentPlanner creates step-by-step logic for each task
- Plan is added to each task description
- Uses `gpt-4o-mini` by default (configurable via `planning_llm`)

**Configuration:**
- `planning=True` - Enable planning for the crew
- `planning_llm` - Specify LLM for the AgentPlanner

**Our Usage:**
- Enable for Research Crew (plan scraping strategy across multiple platforms)
- Enable for Voice AI Crew (plan conversation approach before calls)

---

## 7. Custom Tools

CrewAI allows creating custom tools using two approaches.

**Method 1: @tool Decorator**
- Define tool attributes and functionality directly within a function
- Concise and efficient for simple tools
- Requires: name, description, function logic

**Method 2: BaseTool Subclass**
- Create class inheriting from BaseTool
- Define name, description, and `_run` method
- Better for complex tools with state or multiple methods

**Tool Features:**
- Async support via `async def _run()`
- Error handling and retries
- Input validation
- Caching support

**Our Usage:**
- Firecrawl scraping tool (Research Agent)
- Google Maps proximity tool (Location Analyzer)
- Voice AI call tools (Inspector/Negotiator agents)

---

## 8. Task Guardrails

Guardrails validate and transform task outputs before passing to next task.

**Two Types:**
1. **Function-based guardrails**: Python functions with custom validation logic
   - Return `(True, result)` for success
   - Return `(False, "error message")` for failure
   
2. **LLM-based guardrails**: String descriptions using agent's LLM for validation
   - Ideal for complex or subjective validation
   - Requires agent to be assigned to task

**Configuration:**
- `guardrail` - Single guardrail function or string
- `guardrails` - List of multiple guardrails
- `guardrail_max_retries` - Max retries on validation failure (default: 3)

**Our Usage:**
- Validate property data extraction completeness
- Validate phone number formats before Voice AI calls
- Validate location analysis results contain required amenities

---

## 9. Human Input on Execution

Human input allows agents to request additional information or clarification during task execution.

**How It Works:**
- Set `human_input=True` in task definition
- Agent prompts user for input before delivering final answer
- Input provides extra context, clarifies ambiguities, or validates output

**Use Cases:**
- Complex decision-making scenarios
- Sensitive or high-stakes operations
- Quality assurance and validation
- Creative tasks requiring human judgment

**Our Usage:**
- Human Decision Gate (approve/reject properties before costly Voice AI calls)
- Validate engagement intent (Inspector vs Negotiator path)
- Review and approve final reports before delivery

---

## 10. Replay Tasks from Latest Crew Kickoff

Replay allows re-running tasks from a specific point in the latest crew execution.

**How It Works:**
- Must run `crew.kickoff()` first
- System stores task outputs from latest kickoff
- Can replay from any task, including all subsequent tasks
- Retains context from previously executed tasks

**CLI Commands:**
- `crewai log-tasks-outputs` - View latest kickoff task IDs
- `crewai replay -t <task_id>` - Replay from specific task

**Benefits:**
- Retry failed tasks without re-fetching data
- Debug specific workflow stages
- Resume interrupted workflows

**Our Usage:**
- Replay Voice AI calls that failed to connect
- Retry location analysis with updated parameters
- Resume workflow after human approval gate

---

## 11. LLM Call Hooks and Tool Call Hooks

Execution hooks provide fine-grained control over LLM and tool interactions.

**LLM Call Hooks:**
- `@before_llm_call` - Intercept before LLM execution
  - Modify prompts, validate inputs, implement approval gates
  - Return `False` to block execution
- `@after_llm_call` - Intercept after LLM response
  - Transform responses, sanitize outputs, log results
  - Return modified response or None

**Tool Call Hooks:**
- `@before_tool_call` - Intercept before tool execution
  - Validate parameters, block dangerous operations
  - Return `False` to block execution
- `@after_tool_call` - Intercept after tool completion
  - Transform results, sanitize outputs, log execution
  - Return modified result or None

**Use Cases:**
- Iteration limiting (prevent infinite loops)
- Cost tracking and token usage monitoring
- Response sanitization and content filtering
- Safety guardrails for destructive operations
- Debug logging and monitoring

**Our Usage:**
- Log all Voice AI tool calls for compliance
- Sanitize PII from LLM responses
- Block dangerous operations (data deletion)
- Track API usage and costs across crews
