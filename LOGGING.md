# Logging Configuration - Universal Data Migration Project

## Overview

This project uses Python's built-in `logging` module with a centralized configuration for consistent error tracking, debugging, and monitoring across all modules.

## Features

- **Centralized Configuration** (`logging_config.py`): Single source of truth for logging setup
- **File & Console Handlers**: Logs written to both `logs/` directory and console output
- **Rotating File Handler**: Automatically rotates log files at 10 MB (keeps 5 backups)
- **Detailed Formatting**: Includes timestamp, module name, level, filename, and line number
- **Multi-Module Support**: All key modules are instrumented with logging

## Log Files

Log files are stored in the `logs/` directory with names matching their module:
- `logs/__main__.log` - Main entry point (schema_generator_main.py)
- `logs/connection.log` - Database connection manager
- `logs/database.log` - Database configuration
- `logs/allTableExtractor.log` - Table extraction
- `logs/schema_generator.log` - Schema extraction

### Example Log Entry

```
2026-04-11 13:45:53 - __main__ - INFO - [schema_generator_main.py:83] - Starting data extraction: schema=schema/extracted_schema.json, output=data/values_dump.json, batch_size=2, row_limit=2
```

Format: `TIMESTAMP - LOGGER_NAME - LEVEL - [FILE:LINE] - MESSAGE`

## Usage

### Basic Setup

All scripts using logging need to initialize the configuration once:

```python
from logging_config import setup_logging

# At the start of main() or module load
setup_logging(__name__, log_dir="logs", level=logging.INFO)
```

### Getting a Logger

In any module, get a logger instance:

```python
import logging
logger = logging.getLogger(__name__)

# Use it
logger.info("Application started")
logger.debug("Debug information")
logger.warning("Warning message")
logger.error("Error occurred", exc_info=True)
```

### Log Levels

- **DEBUG**: Detailed diagnostic information (for developers)
- **INFO**: General informational messages
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages with full traceback (when exc_info=True)
- **CRITICAL**: Critical errors that may stop execution

## Instrumented Modules

All key modules now include logging:

### 1. `migrator/connection.py`
- Configuration loading
- Engine creation and disposal
- Connection acquisition and testing

### 2. `migrator/database.py`
- Config file loading
- Connection creation by database type
- PostgreSQL and MySQL-specific connection logging

### 3. `extractor/allTableExtractor.py`
- Table extractor initialization
- Schema discovery
- Column information retrieval

### 4. `schema_generator.py`
- Schema extraction start/end
- Database metadata collection
- File save operations

### 5. `schema_generator_main.py`
- Data extraction workflow
- Table-by-table processing
- Row fetching and file writing

## Log Levels Used

| Module | Level | Purpose |
|--------|-------|---------|
| connection.py | INFO | Engine lifecycle |
| connection.py | DEBUG | Connection details |
| database.py | INFO | Config loading |
| database.py | DEBUG | Connection creation |
| allTableExtractor.py | INFO | Schema discovery |
| allTableExtractor.py | DEBUG | Column retrieval |
| schema_generator.py | INFO | Extraction progress |
| schema_generator_main.py | INFO | Workflow progress |
| All | ERROR | Exceptions with stack traces |

## Error Handling

All critical operations log errors with full exception information:

```python
try:
    risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    raise
```

This ensures:
- Full stack trace is captured in log files
- Error message is human-readable
- Issue can be debugged later by reviewing logs

## Example: Running with Logging

```bash
# Run schema generator with logging
python schema_generator_main.py --config db_config.json --batch-size 1000

# Check console output for INFO and ERROR messages
# Review detailed logs in logs/__main__.log
```

## Troubleshooting

### Logs Not Written

1. Verify `logs/` directory exists and is writable
2. Check filesystem permissions
3. Enable DEBUG level: `setup_logging(__name__, level=logging.DEBUG)`

### Too Much Log Output

1. Reduce verbosity by using `logging.WARNING` level
2. Disable DEBUG logs: `setup_logging(__name__, level=logging.INFO)`
3. Filter specific modules in logging configuration

### Rotating Files Not Working

- Log files rotate automatically at 10 MB
- Old logs backed up as `.log.1`, `.log.2`, etc.
- Only 5 backup files kept per logger

## Configuration Customization

To customize logging (e.g., change log directory):

```python
from logging_config import setup_logging, get_logger

# Custom log directory
setup_logging(__name__, log_dir="custom_logs", level=logging.DEBUG)

# Get logger later
logger = get_logger(__name__)
```

## Best Practices

1. **Always use module name**: `logger = logging.getLogger(__name__)`
2. **Log at appropriate level**: DEBUG for details, INFO for milestones, ERROR for failures
3. **Include context**: Add relevant variables to error messages
4. **Use exc_info=True**: For exception logging to capture stack traces
5. **Avoid log spam**: Don't log in tight loops; instead log summaries
6. **Clean up old logs**: Monitor disk usage in `logs/` directory

## Future Enhancements

- Add log filtering by module
- Implement structured logging (JSON format)
- Add email alerts for critical errors
- Integrate with centralized logging (e.g., ELK stack)
