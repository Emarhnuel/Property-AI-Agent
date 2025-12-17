# Python CrewAI Patterns and Best Practices

## CrewAI Project Structure Conventions

### Standard Project Layout
```
project_root/
├── src/
│   ├── crews/                    # Crew definitions
│   │   ├── __init__.py
│   │   └── my_crew/
│   │       ├── __init__.py
│   │       ├── crew.py           # Main crew class
│   │       ├── agents.py         # Agent definitions
│   │       ├── tasks.py          # Task definitions
│   │       └── config/
│   │           ├── agents.yaml   # Agent configurations
│   │           └── tasks.yaml    # Task configurations
│   ├── tools/                    # Custom tools
│   │   ├── __init__.py
│   │   └── custom_tools.py
│   ├── flows/                    # CrewAI Flows
│   │   ├── __init__.py
│   │   └── main_flow.py
│   └── models/                   # Pydantic models
│       ├── __init__.py
│       └── data_models.py
├── config/
│   ├── settings.py              # Environment settings
│   └── llm_config.yaml          # LLM configurations
├── tests/
│   ├── unit/                    # Unit tests
│   ├── property/                # Property-based tests
│   └── integration/             # Integration tests
└── pyproject.toml
```

### Crew Class Pattern
```python
from crewai import Crew, Agent, Task
from crewai.process import Process

class MyCrew:
    def __init__(self):
        self.agents_config = self.load_config('config/agents.yaml')
        self.tasks_config = self.load_config('config/tasks.yaml')
    
    def create_agents(self):
        return [
            Agent(
                config=self.agents_config['researcher'],
                tools=self.get_research_tools(),
                memory=True,
                verbose=True
            ),
            # More agents...
        ]
    
    def create_tasks(self):
        agents = self.create_agents()
        return [
            Task(
                config=self.tasks_config['research_task'],
                agent=agents[0],
                human_input=False
            ),
            # More tasks...
        ]
    
    def crew(self) -> Crew:
        return Crew(
            agents=self.create_agents(),
            tasks=self.create_tasks(),
            process=Process.Sequential,  # or Process.Hierarchical
            memory=True,
            verbose=True
        )
```

## Pydantic Model Patterns for Data Validation

### Base Model Pattern
```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

class BaseDataModel(BaseModel):
    """Base model with common fields and configurations"""
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    class Config:
        # Allow extra fields for flexibility
        extra = "allow"
        # Use enum values instead of names
        use_enum_values = True
        # Validate assignment
        validate_assignment = True
        # JSON encoders for custom types
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v)
        }
```

### Domain Model Patterns
```python
from enum import Enum
from pydantic import validator, root_validator

class PropertyType(str, Enum):
    HOUSE = "house"
    APARTMENT = "apartment"
    CONDO = "condo"
    TOWNHOUSE = "townhouse"

class SearchCriteria(BaseDataModel):
    location: str = Field(..., min_length=1, description="Search location")
    property_type: Optional[PropertyType] = None
    bedrooms: Optional[int] = Field(None, ge=0, le=20)
    bathrooms: Optional[float] = Field(None, ge=0, le=20)
    price_min: Optional[Decimal] = Field(None, ge=0)
    price_max: Optional[Decimal] = Field(None, ge=0)
    
    @validator('price_max')
    def validate_price_range(cls, v, values):
        if v and values.get('price_min') and v < values['price_min']:
            raise ValueError('price_max must be greater than price_min')
        return v
    
    @root_validator
    def validate_search_criteria(cls, values):
        # Complex validation logic across multiple fields
        return values

class PropertyRecord(BaseDataModel):
    id: str = Field(..., description="Unique property identifier")
    address: str = Field(..., min_length=1)
    specifications: Dict[str, Any] = Field(default_factory=dict)
    image_urls: List[str] = Field(default_factory=list)
    contact_info: Optional[Dict[str, str]] = None
    listing_url: str = Field(..., regex=r'^https?://')
    
    @validator('image_urls')
    def validate_image_urls(cls, v):
        for url in v:
            if not url.startswith(('http://', 'https://')):
                raise ValueError(f'Invalid image URL: {url}')
        return v
```

### Task Output Models
```python
class TaskOutput(BaseDataModel):
    """Standard task output format"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @classmethod
    def success_result(cls, data: Dict[str, Any], **metadata):
        return cls(success=True, data=data, metadata=metadata)
    
    @classmethod
    def error_result(cls, error: str, **metadata):
        return cls(success=False, error_message=error, metadata=metadata)
```

## YAML Configuration Best Practices

### Agent Configuration Pattern
```yaml
# config/agents.yaml
researcher:
  role: "Real Estate Research Specialist"
  goal: "Extract comprehensive property data from real estate platforms"
  backstory: |
    You are an expert real estate researcher with deep knowledge of property 
    markets and data extraction techniques. You excel at finding detailed 
    property information and contact details from various listing platforms.
  max_iter: 3
  max_execution_time: 300
  allow_delegation: false
  memory: true
  verbose: true
  llm:
    model: "gpt-4"
    temperature: 0.1

location_analyzer:
  role: "Location Intelligence Analyst"
  goal: "Analyze property locations and provide proximity insights"
  backstory: |
    You are a geospatial analysis expert who specializes in evaluating 
    property locations based on amenity proximity and neighborhood characteristics.
  max_iter: 2
  max_execution_time: 180
  allow_delegation: false
  memory: true
  verbose: true
  llm:
    model: "gpt-3.5-turbo"
    temperature: 0.0
```

### Task Configuration Pattern
```yaml
# config/tasks.yaml
research_task:
  description: |
    Extract comprehensive property data from the provided search criteria.
    Include property specifications, contact information, and image URLs.
  expected_output: |
    A structured list of PropertyRecord objects containing:
    - Property specifications (bedrooms, bathrooms, price, etc.)
    - Contact information (agent name, phone, email)
    - Image URLs for frontend display
    - Listing URL for reference
  human_input: false
  async_execution: false
  context: []
  output_file: "research_results.json"

approval_gate_task:
  description: |
    Present extracted properties to the user for approval decisions.
    Collect individual property approvals and engagement intent.
  expected_output: |
    A list of PropertyApproval objects with user decisions and preferences.
  human_input: true
  async_execution: false
  context: ["research_task"]
```

### LLM Configuration Pattern
```yaml
# config/llm_config.yaml
default_llm:
  model: "gpt-4"
  temperature: 0.1
  max_tokens: 2000
  timeout: 30

specialized_llms:
  research_llm:
    model: "gpt-4"
    temperature: 0.0  # Deterministic for data extraction
    max_tokens: 3000
  
  conversation_llm:
    model: "gpt-3.5-turbo"
    temperature: 0.7  # More creative for conversations
    max_tokens: 1500
  
  analysis_llm:
    model: "gpt-4"
    temperature: 0.2
    max_tokens: 2500
```

## Error Handling Patterns

### Crew-Level Error Handling
```python
import logging
from typing import Optional
from crewai.crew import CrewOutput

logger = logging.getLogger(__name__)

class CrewExecutionError(Exception):
    """Custom exception for crew execution failures"""
    def __init__(self, message: str, crew_name: str, task_name: Optional[str] = None):
        self.crew_name = crew_name
        self.task_name = task_name
        super().__init__(message)

class RobustCrew:
    def __init__(self, name: str):
        self.name = name
        self.max_retries = 3
        self.retry_delay = 5
    
    def execute_with_retry(self, inputs: Dict[str, Any]) -> CrewOutput:
        """Execute crew with retry logic and error handling"""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Executing {self.name}, attempt {attempt + 1}")
                result = self.crew().kickoff(inputs=inputs)
                
                if self.validate_output(result):
                    return result
                else:
                    raise CrewExecutionError(
                        f"Invalid output from {self.name}",
                        self.name
                    )
                    
            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    
        raise CrewExecutionError(
            f"All {self.max_retries} attempts failed. Last error: {str(last_error)}",
            self.name
        ) from last_error
    
    def validate_output(self, output: CrewOutput) -> bool:
        """Validate crew output meets requirements"""
        try:
            # Implement validation logic
            return output and hasattr(output, 'raw')
        except Exception as e:
            logger.error(f"Output validation failed: {str(e)}")
            return False
```

### Task-Level Error Handling
```python
from crewai import Task
from functools import wraps

def handle_task_errors(func):
    """Decorator for task error handling"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Task {func.__name__} failed: {str(e)}")
            return TaskOutput.error_result(
                error=str(e),
                task_name=func.__name__,
                timestamp=datetime.now().isoformat()
            )
    return wrapper

@handle_task_errors
def create_research_task(agent, config):
    """Create research task with error handling"""
    return Task(
        description=config['description'],
        expected_output=config['expected_output'],
        agent=agent,
        tools=get_research_tools()
    )
```

### Tool Error Handling
```python
from crewai_tools import BaseTool
from typing import Any

class RobustTool(BaseTool):
    """Base tool class with error handling"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_retries = 3
        self.timeout = 30
    
    def _run(self, *args, **kwargs) -> Any:
        """Execute tool with error handling and retries"""
        for attempt in range(self.max_retries):
            try:
                return self._execute(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Tool {self.name} attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(1 * (attempt + 1))
    
    def _execute(self, *args, **kwargs) -> Any:
        """Override this method in subclasses"""
        raise NotImplementedError
```

## Testing Strategies (Unit + Property-Based)

### Unit Testing Pattern
```python
import pytest
from unittest.mock import Mock, patch
from crewai import Agent, Task, Crew

class TestResearchCrew:
    @pytest.fixture
    def mock_agent(self):
        return Mock(spec=Agent)
    
    @pytest.fixture
    def mock_task(self):
        return Mock(spec=Task)
    
    @pytest.fixture
    def research_crew(self, mock_agent, mock_task):
        with patch('my_crew.crew.Agent', return_value=mock_agent), \
             patch('my_crew.crew.Task', return_value=mock_task):
            return ResearchCrew()
    
    def test_crew_creation(self, research_crew):
        """Test crew is created with correct configuration"""
        crew = research_crew.crew()
        assert crew is not None
        assert len(crew.agents) > 0
        assert len(crew.tasks) > 0
    
    @patch('my_crew.tools.firecrawl_tool')
    def test_research_task_execution(self, mock_tool, research_crew):
        """Test research task executes successfully"""
        mock_tool.return_value = {"properties": []}
        
        result = research_crew.execute_with_retry({
            "search_criteria": {"location": "New York"}
        })
        
        assert result is not None
        mock_tool.assert_called_once()
    
    def test_error_handling(self, research_crew):
        """Test crew handles errors gracefully"""
        with patch.object(research_crew.crew(), 'kickoff', side_effect=Exception("Test error")):
            with pytest.raises(CrewExecutionError):
                research_crew.execute_with_retry({})
```

### Property-Based Testing Pattern
```python
from hypothesis import given, strategies as st, settings
from hypothesis.strategies import composite
import pytest

# Custom generators for domain objects
@composite
def search_criteria_generator(draw):
    """Generate valid SearchCriteria objects"""
    return SearchCriteria(
        location=draw(st.text(min_size=1, max_size=100)),
        property_type=draw(st.sampled_from(PropertyType) | st.none()),
        bedrooms=draw(st.integers(min_value=0, max_value=20) | st.none()),
        bathrooms=draw(st.floats(min_value=0, max_value=20) | st.none()),
        price_min=draw(st.decimals(min_value=0, max_value=10000000) | st.none()),
        price_max=draw(st.decimals(min_value=0, max_value=10000000) | st.none())
    )

@composite
def property_record_generator(draw):
    """Generate valid PropertyRecord objects"""
    return PropertyRecord(
        id=draw(st.text(min_size=1, max_size=50)),
        address=draw(st.text(min_size=10, max_size=200)),
        specifications=draw(st.dictionaries(st.text(), st.text())),
        image_urls=draw(st.lists(st.text().filter(lambda x: x.startswith('http')))),
        listing_url=draw(st.text().filter(lambda x: x.startswith('http')))
    )

class TestPropertyBasedValidation:
    @given(search_criteria=search_criteria_generator())
    @settings(max_examples=100)
    def test_search_criteria_processing_property(self, search_criteria):
        """**Feature: ai-real-estate-agent, Property 1: Search Criteria Processing**
        
        For any valid search criteria input, the system should initiate 
        Research_Agent deployment with parameters that match the specified criteria.
        """
        # Test that search criteria always result in appropriate agent deployment
        crew = ResearchCrew()
        
        # Mock the crew execution
        with patch.object(crew, 'crew') as mock_crew:
            mock_crew.return_value.kickoff.return_value = Mock()
            
            result = crew.execute_with_retry({"search_criteria": search_criteria.dict()})
            
            # Verify crew was called with correct parameters
            mock_crew.return_value.kickoff.assert_called_once()
            call_args = mock_crew.return_value.kickoff.call_args[1]['inputs']
            assert 'search_criteria' in call_args
            assert call_args['search_criteria']['location'] == search_criteria.location
    
    @given(property_records=st.lists(property_record_generator(), min_size=1, max_size=10))
    @settings(max_examples=50)
    def test_approval_workflow_integrity_property(self, property_records):
        """**Feature: ai-real-estate-agent, Property 4: Frontend Approval Workflow**
        
        For any set of extracted properties, the frontend interface should 
        display all properties and accept individual approval decisions.
        """
        approval_gate = ApprovalGate()
        
        # Test that all properties are presented for approval
        presented_properties = approval_gate.present_properties(property_records)
        assert len(presented_properties) == len(property_records)
        
        # Test that approval decisions are properly collected
        approvals = [PropertyApproval(property_id=p.id, approved=True) 
                    for p in property_records[:len(property_records)//2]]
        
        approved_ids = approval_gate.process_approvals(approvals)
        assert len(approved_ids) == len(approvals)
        assert all(approval.property_id in approved_ids for approval in approvals)

# Test configuration
pytest_plugins = ["hypothesis.extra.pytest"]

# Custom Hypothesis settings
settings.register_profile("ci", max_examples=200, deadline=None)
settings.register_profile("dev", max_examples=50, deadline=None)
```

### Integration Testing Pattern
```python
import pytest
from testcontainers import compose
import requests
import time

class TestIntegration:
    @pytest.fixture(scope="class")
    def docker_services(self):
        """Start external services for integration testing"""
        with compose.DockerCompose("tests/docker-compose.test.yml") as compose:
            # Wait for services to be ready
            time.sleep(10)
            yield compose
    
    def test_end_to_end_workflow(self, docker_services):
        """Test complete workflow with real external services"""
        # Test with actual Firecrawl, Google Maps, etc.
        search_criteria = SearchCriteria(
            location="San Francisco, CA",
            property_type=PropertyType.APARTMENT,
            bedrooms=2
        )
        
        crew = ResearchCrew()
        result = crew.execute_with_retry({"search_criteria": search_criteria.dict()})
        
        assert result is not None
        assert len(result.raw) > 0
    
    @pytest.mark.slow
    def test_background_operations(self):
        """Test background operation capabilities"""
        # Test that crew can operate independently
        pass
```

### Test Organization
```python
# conftest.py - Shared test configuration
import pytest
from unittest.mock import Mock

@pytest.fixture(scope="session")
def test_config():
    """Test configuration settings"""
    return {
        "firecrawl_api_key": "test_key",
        "google_maps_api_key": "test_key",
        "voice_ai_api_key": "test_key"
    }

@pytest.fixture
def mock_external_services():
    """Mock all external service calls"""
    with patch('firecrawl.FirecrawlApp') as mock_firecrawl, \
         patch('googlemaps.Client') as mock_maps, \
         patch('voice_ai.VoiceClient') as mock_voice:
        
        yield {
            'firecrawl': mock_firecrawl,
            'maps': mock_maps,
            'voice': mock_voice
        }
```

## Additional Best Practices

### Memory Management
```python
# Configure memory for agents
agent = Agent(
    role="Research Specialist",
    memory=True,  # Enable memory
    verbose=True
)

# Access memory in tools
from crewai.memory import ShortTermMemory, LongTermMemory

class MemoryAwareTool(BaseTool):
    def _run(self, query: str) -> str:
        # Access agent's memory
        memory = self.agent.memory
        previous_results = memory.search(query)
        # Use previous results to inform current execution
```

### Execution Hooks
```python
from crewai import before_llm_call, after_llm_call

@before_llm_call
def log_llm_call(llm, messages, **kwargs):
    """Log LLM calls for debugging"""
    logger.info(f"LLM call: {llm.model_name}, messages: {len(messages)}")
    return messages

@after_llm_call
def validate_llm_response(llm, messages, response, **kwargs):
    """Validate LLM responses"""
    if not response or len(response.strip()) < 10:
        logger.warning("LLM response too short")
    return response
```

### Flow Integration
```python
from crewai.flow import Flow, listen, start

class RealEstateFlow(Flow):
    @start()
    def initiate_search(self):
        # Start the workflow
        return "search_initiated"
    
    @listen("search_initiated")
    def extract_properties(self):
        # Execute research crew
        crew = ResearchCrew()
        return crew.execute_with_retry(self.state)
    
    @listen("properties_extracted")
    def human_approval(self):
        # Human decision gate
        return self.collect_approvals()
```