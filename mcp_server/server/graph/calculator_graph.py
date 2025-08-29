from langgraph.graph import StateGraph

from mcp_server.server.agents.calculation_validator_agent import CalculationValidatorAgent
from mcp_server.server.agents.calculator_agent import CalculatorAgent
from mcp_server.server.schemas.calculator_state import CalculatorState


class CalculatorGraph:
    def __init__(self):
        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(CalculatorState)
        builder.add_node("calculator", self.calculator_node)
        builder.add_node("validation", self.validation_node)

        builder.set_entry_point("calculator")
        builder.add_edge("calculator", "validation")
        builder.set_finish_point("validation")

        return builder.compile()

    @staticmethod
    def calculator_node(state: CalculatorState) -> CalculatorState:
        calculator_agent = CalculatorAgent()
        response = calculator_agent.calculate_expression(query=state["query"])
        state["calculated_results"] = response
        return state

    @staticmethod
    def validation_node(state: CalculatorState) -> CalculatorState:
        validator_agent = CalculationValidatorAgent()
        response = validator_agent.validate_calculation(calculated_result=state["calculated_results"])
        state["validated_results"] = response
        return state

    def run(self, query: str):
        input_state = CalculatorState(query=query)

        output_state = self.graph.invoke(input_state)
        return output_state["validated_results"]
