# Implementation Plan

- [ ] 1. Set up project structure and core interfaces
  - Create directory structure for flows, agents, services, and models
  - Set up CrewAI Flows project with proper configuration
  - Define core Pydantic data models (SearchCriteria, PropertyRecord, LocationIntelligence, CallResult)
  - Configure testing framework with Hypothesis for property-based testing
  - Set up environment configuration for API keys and service endpoints
  - _Requirements: 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 7.1, 8.1_

- [ ]* 1.1 Write property test for search criteria processing
  - **Property 1: Search Criteria Processing**
  - **Validates: Requirements 1.1, 1.2, 1.3**

- [ ]* 1.2 Write property test for input validation and format support
  - **Property 2: Input Validation and Format Support**
  - **Validates: Requirements 1.4, 1.5**

- [ ] 2. Implement core data models and validation
  - Create PropertyRecord, SearchCriteria, and LocationIntelligence models
  - Implement data validation rules and serialization methods
  - Create ContactInfo and CallResult models with image URL handling
  - Add model validation for phone numbers, addresses, and coordinates
  - _Requirements: 2.1, 2.2, 2.3, 3.2, 4.4, 5.5, 6.5, 7.2_

- [ ]* 2.1 Write property test for comprehensive data extraction
  - **Property 3: Comprehensive Data Extraction**
  - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**

- [ ] 3. Create Flow Controller and background operations
  - Implement CrewAI Flow class with structured state management
  - Create workflow phase management and state transitions
  - Implement background operation capabilities for autonomous processing
  - Add user account integration for report storage
  - _Requirements: 7.1, 7.2, 7.3_

- [ ] 4. Implement Research Agent crew
  - Create Research Agent using CrewAI with Firecrawl integration
  - Implement property listing scraping with dynamic content rendering
  - Add contact information extraction from listings
  - Create image URL extraction for frontend display
  - Implement error handling for scraping failures and missing data
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ]* 4.1 Write unit tests for Research Agent crew
  - Test Firecrawl integration with mock responses
  - Test contact extraction accuracy
  - Test image URL extraction functionality
  - Test error handling for malformed listings
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ] 5. Implement Frontend Decision Interface
  - Create frontend interface for property presentation with image URLs
  - Implement property approval/rejection collection in user interface
  - Add validation for approval decisions
  - Create workflow termination logic for no approvals
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ]* 5.1 Write property test for frontend approval workflow
  - **Property 4: Frontend Approval Workflow**
  - **Validates: Requirements 3.1, 3.2, 3.3, 3.4**

- [ ] 6. Implement Location Analyzer
  - Create Google Maps API integration for proximity analysis
  - Implement distance calculations for markets, gyms, bus parks, railway terminals, stadiums, malls, airports, and seaports
  - Add 6km radius filtering for amenity searches
  - Create structured amenity scores with proximity data
  - Implement graceful handling of missing mapping data
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ]* 6.1 Write property test for amenity proximity analysis
  - **Property 5: Amenity Proximity Analysis**
  - **Validates: Requirements 4.1, 4.2, 4.3, 4.4**

- [ ] 7. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Implement Voice AI service integration
  - Create base Voice AI service with Vapi/Retell integration
  - Implement phone call initiation and menu navigation
  - Add conversation flow management and transcript recording
  - Create background retry logic for failed calls (retry after several hours)
  - _Requirements: 5.2, 5.3, 5.5, 6.2, 6.3, 6.5, 7.1_

- [ ]* 8.1 Write unit tests for Voice AI service
  - Test phone call initiation with mock Voice AI API
  - Test menu navigation logic
  - Test conversation recording and transcript generation
  - Test background retry logic for call failures
  - _Requirements: 5.2, 5.3, 5.5, 6.2, 6.3, 6.5, 7.1_

- [ ] 9. Implement Inspector AI agent
  - Create Inspector AI for rental/purchase property interactions
  - Implement inspection booking conversation flows
  - Add user-defined question execution during calls
  - Create booking confirmation capture and validation
  - _Requirements: 5.1, 5.3, 5.4, 5.5_

- [ ]* 9.1 Write property test for Inspector AI engagement
  - **Property 6: Inspector AI Engagement**
  - **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**

- [ ] 10. Implement Negotiator AI agent
  - Create Negotiator AI for acquisition property interactions
  - Implement persuasive conversation techniques for owner engagement
  - Add interest assessment and negotiation initiation logic
  - Create graceful conversation termination for disinterested owners
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ]* 10.1 Write property test for Negotiator AI engagement
  - **Property 7: Negotiator AI Engagement**
  - **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5**

- [ ] 11. Implement engagement routing logic
  - Create intent detection for rental/purchase vs acquisition
  - Implement workflow branching to Inspector or Negotiator paths
  - Add engagement path validation and error handling
  - _Requirements: 5.1, 6.1_

- [ ] 12. Implement report generation and user account system
  - Create Unified Report compilation from all workflow data
  - Implement user account storage for completed reports
  - Add call recording and transcript inclusion in reports
  - Create structured report output with all required elements
  - _Requirements: 7.3, 7.5_

- [ ]* 12.1 Write property test for background operations and notifications
  - **Property 8: Background Operations and Notifications**
  - **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5**

- [ ] 13. Implement notification system
  - Create email notification service for report completion
  - Implement WhatsApp notification integration
  - Add notification triggers when reports are ready in user accounts
  - Create notification preference handling
  - _Requirements: 7.4, 7.5_

- [ ]* 13.1 Write unit tests for notification system
  - Test email notification with mock SMTP service
  - Test WhatsApp notification integration with mock API
  - Test user account report storage functionality
  - Test notification triggers and preferences
  - _Requirements: 7.4, 7.5_

- [ ] 14. Implement privacy and security features
  - Create call recording consent mechanisms
  - Implement data encryption for storage and transmission
  - Add privacy regulation compliance checks
  - Create data deletion functionality for user requests
  - Implement incident response procedures for data breaches
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ]* 14.1 Write property test for privacy and security compliance
  - **Property 9: Privacy and Security Compliance**
  - **Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5**

- [ ] 15. Integrate all components into main workflow
  - Wire Flow Controller with all agent crews and services
  - Implement complete workflow orchestration from search to notification
  - Add background operation coordination across all phases
  - Create workflow execution monitoring and logging
  - _Requirements: All requirements integration_

- [ ]* 15.1 Write integration tests for complete workflow
  - Test end-to-end workflow execution with mock services
  - Test error propagation and recovery across phases
  - Test state persistence and restoration
  - Test concurrent workflow execution
  - _Requirements: All requirements integration_

- [ ] 16. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.