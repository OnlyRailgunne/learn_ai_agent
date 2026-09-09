from core.event import (
    NodeExecutionEvent,
    TransitionEvent,
    PlanningChoiceEvent
)


class History:

    def __init__(self):
        self.events = []
        self.snapshots = {}

    def add(self, event):
        self.events.append(event)

    def add_snapshot(self, snapshot):

        if not self.events:
            return False

        event_index = len(self.events) - 1

        self.snapshots[event_index] = snapshot

        return True

    def latest_snapshot(self):

        if not self.snapshots:
            return None

        latest_index = max(
            self.snapshots.keys()
        )

        return (
            latest_index,
            self.snapshots[latest_index]
        )

    def latest_node_execution(self):

        for index in range(
            len(self.events) - 1,
            -1,
            -1
        ):

            event = self.events[index]

            if isinstance(
                event,
                NodeExecutionEvent
            ):
                return (
                    index,
                    event
                )

        return None

    def snapshot_position(
        self,
        event_index
    ):

        event = self.events[event_index]

        if isinstance(
            event,
            TransitionEvent
        ):
            return event.target

        return None

    def events_after(
        self,
        event_index
    ):
        return self.events[
            event_index + 1:
        ]

    def transitions_after(
        self,
        event_index
    ):

        transitions = []

        for event in self.events[
            event_index + 1:
        ]:

            if isinstance(
                event,
                TransitionEvent
            ):
                transitions.append(
                    event
                )

        return transitions

    def previous_transition(
        self,
        event_index
    ):

        for index in range(
            event_index - 1,
            -1,
            -1
        ):

            event = self.events[index]

            if isinstance(
                event,
                TransitionEvent
            ):
                return (
                    index,
                    event
                )

        return None

    def snapshot_before(
        self,
        event_index
    ):

        candidates = [
            index
            for index
            in self.snapshots.keys()
            if index < event_index
        ]

        if not candidates:
            return None

        latest_index = max(
            candidates
        )

        return (
            latest_index,
            self.snapshots[latest_index]
        )

    def previous_graph_transition(
        self,
        event_index,
        graph=None
    ):
    
        for index in range(
            event_index - 1,
            -1,
            -1
        ):
    
            event = self.events[index]
    
            if not isinstance(
                event,
                TransitionEvent
            ):
                continue
            
            
            # ---------------------------------
            # 优先使用 Transition 当时自己的 Graph
            #
            # graph 参数只作为旧 Event 的兼容 fallback
            # ---------------------------------
    
            event_graph = (
                event.graph
                if event.graph is not None
                else graph
            )
    
            if event_graph is None:
                continue
            
            
            # ---------------------------------
            # 只有真正属于当时 Graph Edge 的
            # Transition 才算 Graph Transition
            # ---------------------------------
    
            if event_graph.has_edge(
                event.source,
                event.target
            ):
    
                return (
                    index,
                    event
                )
    
    
        return (
            None,
            None
        )
    
    def targets_from(
        self,
        source
    ):

        targets = []

        for event in self.events:

            # 正常 Graph 路径
            if isinstance(
                event,
                TransitionEvent
            ):

                if event.source == source:
                    targets.append(
                        event.target
                    )

            # Replan 选择的路径
            if isinstance(
                event,
                PlanningChoiceEvent
            ):

                if event.source == source:
                    targets.append(
                        event.target
                    )

        return targets