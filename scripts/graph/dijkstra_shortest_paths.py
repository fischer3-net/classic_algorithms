from __future__ import annotations

import heapq


def dijkstra(graph: dict[str, dict[str, float]], source: str) -> dict[str, float]:
    """Compute shortest-path distances for graphs with non-negative edge weights."""
    nodes = set(graph)
    for neighbors in graph.values():
        for neighbor, weight in neighbors.items():
            if weight < 0:
                raise ValueError("Dijkstra's algorithm requires non-negative edge weights")
            nodes.add(neighbor)

    if source not in nodes:
        raise ValueError(f"Unknown source node: {source}")

    distances = {node: float("inf") for node in nodes}
    distances[source] = 0.0
    queue: list[tuple[float, str]] = [(0.0, source)]

    while queue:
        current_distance, node = heapq.heappop(queue)
        if current_distance > distances[node]:
            continue

        for neighbor, weight in graph.get(node, {}).items():
            candidate = current_distance + weight
            if candidate < distances[neighbor]:
                distances[neighbor] = candidate
                heapq.heappush(queue, (candidate, neighbor))

    return distances


def main() -> None:
    graph = {
        "A": {"B": 4, "C": 2},
        "B": {"A": 4, "C": 1, "D": 5},
        "C": {"A": 2, "B": 1, "D": 8, "E": 10},
        "D": {"B": 5, "C": 8, "E": 2, "F": 6},
        "E": {"C": 10, "D": 2, "F": 3},
        "F": {"D": 6, "E": 3},
    }

    source = "A"
    distances = dijkstra(graph, source)
    print(f"Shortest path distances from {source}:")
    for node, distance in sorted(distances.items()):
        print(f"  {node}: {distance}")


if __name__ == "__main__":
    main()
