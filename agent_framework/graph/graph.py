#graph.py
from graph.edge import Edge


class Graph:

    def __init__(self):
        self._edges = {}

    def connect(
        self,
        current,
        next_node,
        condition=None
    ):
        edge = Edge(
            source=current,
            target=next_node,
            condition=condition
        )

        if current not in self._edges:
            self._edges[current] = []

        self._edges[current].append(edge)

    def next(
        self,
        current,
        state
    ):
        edges = self._edges.get(
            current,
            []
        )

        for edge in edges:

            # 没有 condition
            # 表示无条件可以走
            if edge.condition is None:
                return edge.target

            # 有 condition
            # 当前 State 满足条件才可以走
            if edge.condition(state):
                return edge.target

        return None

    def edges_from(
        self,
        node
    ):
        return self._edges.get(
            node,
            []
        )

    def has_edge(
        self,
        source,
        target
    ):
        edges = self._edges.get(
            source,
            []
        )

        for edge in edges:

            if edge.target == target:
                return True

        return False

    def available_edges_from(
        self,
        node,
        state
    ):
        """
        返回当前 State 下真正可以走的 Edge。

        与 edges_from() 的区别：

        edges_from()
        -> 返回 Graph 结构上所有 Edge

        available_edges_from()
        -> 只返回当前 State 满足 condition 的 Edge
        """

        edges = self._edges.get(
            node,
            []
        )

        available = []

        for edge in edges:

            # 无条件 Edge
            if edge.condition is None:
                available.append(edge)
                continue

            # 有条件 Edge
            if edge.condition(state):
                available.append(edge)

        return available