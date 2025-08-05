# MetricFlow AI

## Overview

MetricFlow AI is an intelligent system for generating metrics, KPIs, and OKRs recommendations based on business initiatives. The application takes natural language descriptions of business initiatives and produces comprehensive metric analysis reports in PDF format. It leverages AI models (Mistral for context analysis and OpenAI GPT-4 for metrics generation) to provide structured recommendations with detailed explanations and justifications.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Modern Streamlit Interface**: Enhanced single-page application with gradient designs, custom CSS styling, and responsive layout
- **Interactive Sidebar**: Step-by-step workflow guide, categorized examples with 8+ pre-defined initiatives, and system statistics
- **Smart Examples System**: Clickable initiative templates organized by categories (Mobile, Analytics, Marketing, etc.)
- **Visual Progress Tracking**: Multi-step progress indicators with descriptive labels and success animations
- **Real-time Validation**: Input validation and sanitization with user-friendly error handling

### Backend Architecture
- **Service-Oriented Design**: Modular services pattern with dedicated classes for each AI provider and PDF generation
- **Two-Stage AI Processing**: 
  - Stage 1: Mistral AI analyzes context and classifies the initiative (type, objective, funnel stage, complexity)
  - Stage 2: OpenAI GPT-4 generates specific metrics, KPIs, and OKRs based on the contextual analysis
- **Template-Based PDF Generation**: HTML templates with CSS styling converted to PDF using WeasyPrint

### Data Flow
1. User submits initiative description
2. Input validation and sanitization
3. Mistral service analyzes context and classifies initiative
4. OpenAI service generates metrics using context from Mistral
5. PDF generator combines results using HTML template
6. Generated PDF delivered to user for download

### Error Handling
- Comprehensive validation for user inputs (length, content, format)
- API key verification for external services
- Exception handling with user-friendly error messages
- Graceful degradation when services are unavailable

## External Dependencies

### AI Services
- **Mistral AI API**: Context analysis and initiative classification using mistral-large-latest model
- **OpenAI API**: Metrics generation using GPT-4o model for KPIs, OKRs, and detailed explanations

### PDF Generation
- **WeasyPrint**: HTML-to-PDF conversion engine for generating formatted reports
- **HTML/CSS Templates**: Custom styling for professional report appearance

### Web Framework
- **Streamlit**: Complete web application framework handling UI, state management, and file downloads

### Environment Configuration
- API keys managed through environment variables (OPENAI_API_KEY, MISTRAL_API_KEY)
- Configurable model selection and API endpoints