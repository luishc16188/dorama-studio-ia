"""Base agent class that all V2 agents must inherit from."""

import abc
import logging
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

InputSchemaType = TypeVar('InputSchemaType', bound=BaseModel)
OutputSchemaType = TypeVar('OutputSchemaType', bound=BaseModel)


class BaseAgent(Generic[InputSchemaType, OutputSchemaType], abc.ABC):
    """
    Base agent class that all V2 agents must inherit from.
    Provides standardized interface for agent execution with input/output validation.
    """

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"agent.{name}")
        self.InputSchema: type[InputSchemaType] | None = None
        self.OutputSchema: type[OutputSchemaType] | None = None

    @abc.abstractmethod
    def run(self, input_data: Any) -> OutputSchemaType:
        """
        Execute the agent with input data.

        Args:
            input_data: Raw input data to be validated and processed

        Returns:
            OutputSchemaType: Validated output according to agent's output schema
        """
        pass

    def process(self, input_data: Any) -> OutputSchemaType:
        """
        Process input data with validation and error handling.

        Args:
            input_data: Raw input data

        Returns:
            OutputSchemaType: Processed output

        Raises:
            ValueError: If input data fails validation
            Exception: For processing errors
        """
        self.logger.info(f"{self.name} starting processing")

        # Validate input if schema is defined
        validated_input = self._validate_input(input_data)

        # Process with implementation-specific logic
        result = self._process(validated_input)

        # Validate output if schema is defined
        validated_output = self._validate_output(result)

        self.logger.info(f"{self.name} processing completed")
        return validated_output

    def _validate_input(self, input_data: Any) -> InputSchemaType:
        """Validate and convert input data to input schema."""
        if self.InputSchema is None:
            # No validation required, return as-is
            return input_data

        if isinstance(input_data, self.InputSchema):
            return input_data

        try:
            return self.InputSchema.model_validate(input_data)
        except Exception as e:
            self.logger.error(f"Input validation failed: {e}")
            raise ValueError(f"Invalid input for {self.name}: {e}")

    def _validate_output(self, output_data: Any) -> OutputSchemaType:
        """Validate and convert output data to output schema."""
        if self.OutputSchema is None:
            # No validation required, return as-is
            return output_data

        if isinstance(output_data, self.OutputSchema):
            return output_data

        try:
            return self.OutputSchema.model_validate(output_data)
        except Exception as e:
            self.logger.error(f"Output validation failed: {e}")
            raise ValueError(f"Invalid output from {self.name}: {e}")

    @abc.abstractmethod
    def _process(self, validated_input: InputSchemaType) -> OutputSchemaType:
        """
        Implementation-specific processing logic.

        Args:
            validated_input: Input data validated against input schema

        Returns:
            OutputSchemaType: Processed output (will be validated against output schema)
        """
        pass

    def quality_gate(self, episode_id: str | None, episode_data: dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Quality Gate - 100 point validation across 15 dimensions.
        Returns (approved, deficiencies).
        """
        checks = [
            ("hook_0_3s", 20),
            ("conflict_concrete", 15),
            ("protagonist_desire_clarified", 15),
            ("unresolved_question", 15),
            ("situation_worsens", 15),
            ("partial_answer", 10),
            ("surprise_element", 10),
            ("strong_cliffhanger", 10),
            ("emotional_impact", 5),
            ("show_dont_tell", 5),
            ("dialogue_advances_story", 5),
            ("dialogue_delivery_present", 5),
            ("micro_expressions_present", 5),
            ("silence_drop_before_revelation", 5),
            ("fractal_formula_applied", 5),
        ]

        score = sum(pts for field, pts in checks if episode_data.get(field))
        approved = score >= 70  # 70% threshold for approval
        deficiencies = [field for field, pts in checks if not episode_data.get(field)]

        return approved, deficiencies
