class NodeResult:
    """Result object returned by a graph node after execution.

    Captures whether the node executed successfully and any output
    data produced during execution.
    """

    def __init__(self, success=True, output=None):
        """Initialize a NodeResult.

        Args:
            success: Whether the node execution succeeded. Defaults to True.
            output: The output data produced by the node. Defaults to None.
        """
        self.success = success
        self.output = output