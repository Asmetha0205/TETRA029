"""
API Controllers for Recommendation Intelligence Layer.
Coordinates incoming HTTP endpoints with underlying service methods.
"""

from typing import Any, Dict, List, Optional
from backend.recommendation_engine.api.schemas import ApiResponse, GenerateRecommendationsApiRequest
from backend.recommendation_engine.graph.graph_service import GraphService
from backend.recommendation_engine.service.recommendation_service import RecommendationService
from backend.recommendation_engine.service.service_models import ExportReportRequest, GenerateRecommendationsRequest


class RecommendationController:
    """
    Controller handling HTTP endpoints for Recommendations and Knowledge Graph.
    """

    def __init__(self, service: RecommendationService, graph_service: GraphService):
        self.service = service
        self.graph_service = graph_service

    def generate_recommendations(self, request: GenerateRecommendationsApiRequest) -> ApiResponse:
        """Handle POST /recommendations/generate."""
        svc_req = GenerateRecommendationsRequest(
            gap_analysis_data=request.gap_analysis_data,
            target_gaps=request.target_gaps,
            knowledge_context=request.knowledge_context
        )
        res = self.service.generate_recommendations(svc_req)
        if not res.success:
            return ApiResponse(status="error", message=res.message)

        return ApiResponse(
            status="success",
            message="Recommendations generated successfully",
            data={
                "recommendations": res.recommendations.model_dump() if res.recommendations else {},
                "learning_path": res.learning_path.model_dump() if res.learning_path else {},
                "executive_summary": res.report.executive_summary if res.report else ""
            }
        )

    def get_all_recommendations(self) -> ApiResponse:
        """Handle GET /recommendations."""
        if self.service._last_result_set:
            return ApiResponse(
                status="success",
                data=self.service._last_result_set.model_dump()
            )
        # Default output
        res = self.service.generate_recommendations(
            GenerateRecommendationsRequest(
                gap_analysis_data={"gap": ["Redis", "Docker", "FastAPI", "Kubernetes"]}
            )
        )
        return ApiResponse(
            status="success",
            data=res.recommendations.model_dump() if res.recommendations else {}
        )

    def get_recommendation_by_id(self, item_id: str) -> ApiResponse:
        """Handle GET /recommendations/{id}."""
        item = self.service.get_recommendation(item_id)
        if item:
            return ApiResponse(status="success", data=item.model_dump())
        return ApiResponse(status="error", message=f"Recommendation for '{item_id}' not found.")

    def get_evidence(self, target_gaps: Optional[List[str]] = None) -> ApiResponse:
        """Handle GET /recommendations/evidence."""
        items = self.service.get_evidence(target_gaps)
        return ApiResponse(
            status="success",
            data=[item.model_dump() for item in items]
        )

    def get_learning_path(self, technologies: Optional[List[str]] = None) -> ApiResponse:
        """Handle GET /recommendations/learning-path."""
        plan = self.service.get_learning_path(technologies)
        return ApiResponse(status="success", data=plan.model_dump())

    def get_report(self, format_type: str = "json") -> ApiResponse:
        """Handle GET /recommendations/report."""
        req = ExportReportRequest(format=format_type)
        res = self.service.export_report(req)
        return ApiResponse(
            status="success",
            data={"format": format_type, "content": res.exported_content}
        )

    def get_graph_summary(self) -> ApiResponse:
        """Handle GET /graph and GET /graph/statistics."""
        stats = self.graph_service.get_statistics()
        return ApiResponse(status="success", data=stats.model_dump())

    def get_graph_node(self, node_id: str) -> ApiResponse:
        """Handle GET /graph/node/{id}."""
        node = self.graph_service.get_node_by_id(node_id)
        if node:
            return ApiResponse(status="success", data=node.model_dump())
        return ApiResponse(status="error", message=f"Node '{node_id}' not found in graph.")

    def search_graph_nodes(self, query: str, limit: int = 20) -> ApiResponse:
        """Handle GET /graph/search."""
        nodes = self.graph_service.search_nodes(query, limit=limit)
        return ApiResponse(status="success", data=[n.model_dump() for n in nodes])
