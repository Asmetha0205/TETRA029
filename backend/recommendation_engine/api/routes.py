"""
FastAPI Routes for Recommendation Intelligence Layer.
Exposes REST endpoints:
- POST /recommendations/generate
- GET /recommendations
- GET /recommendations/{id}
- GET /recommendations/evidence
- GET /recommendations/learning-path
- GET /recommendations/report
- GET /graph
- GET /graph/node/{id}
- GET /graph/search
- GET /graph/statistics
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from backend.recommendation_engine.api.controllers import RecommendationController
from backend.recommendation_engine.api.dependencies import get_graph_service, get_recommendation_service
from backend.recommendation_engine.api.schemas import ApiResponse, GenerateRecommendationsApiRequest
from backend.recommendation_engine.graph.graph_service import GraphService
from backend.recommendation_engine.service.recommendation_service import RecommendationService

router = APIRouter(prefix="", tags=["Recommendations & Knowledge Graph"])


def _get_controller(
    rec_svc: RecommendationService = Depends(get_recommendation_service),
    graph_svc: GraphService = Depends(get_graph_service)
) -> RecommendationController:
    return RecommendationController(rec_svc, graph_svc)


@router.post("/recommendations/generate", response_model=ApiResponse)
def generate_recommendations(
    request: GenerateRecommendationsApiRequest,
    controller: RecommendationController = Depends(_get_controller)
):
    """Generate grounded curriculum recommendations from gap analysis input."""
    return controller.generate_recommendations(request)


@router.get("/recommendations", response_model=ApiResponse)
def get_recommendations(
    controller: RecommendationController = Depends(_get_controller)
):
    """Fetch active session recommendations."""
    return controller.get_all_recommendations()


@router.get("/recommendations/evidence", response_model=ApiResponse)
def get_evidence(
    target_gaps: Optional[List[str]] = Query(default=None),
    controller: RecommendationController = Depends(_get_controller)
):
    """Fetch retrieved graph evidence metrics for gap technologies."""
    return controller.get_evidence(target_gaps)


@router.get("/recommendations/learning-path", response_model=ApiResponse)
def get_learning_path(
    technologies: Optional[List[str]] = Query(default=None),
    controller: RecommendationController = Depends(_get_controller)
):
    """Get dependency-aware technology learning path."""
    return controller.get_learning_path(technologies)


@router.get("/recommendations/report", response_model=ApiResponse)
def get_report(
    format: str = Query(default="json", description="json, markdown, or pdf"),
    controller: RecommendationController = Depends(_get_controller)
):
    """Export formatted executive recommendation report."""
    return controller.get_report(format)


@router.get("/recommendations/{id}", response_model=ApiResponse)
def get_recommendation_by_id(
    id: str,
    controller: RecommendationController = Depends(_get_controller)
):
    """Get recommendation item by technology name or ID."""
    return controller.get_recommendation_by_id(id)


@router.get("/graph", response_model=ApiResponse)
@router.get("/graph/statistics", response_model=ApiResponse)
def get_graph_statistics(
    controller: RecommendationController = Depends(_get_controller)
):
    """Fetch Knowledge Graph statistics and node/relationship counts."""
    return controller.get_graph_summary()


@router.get("/graph/search", response_model=ApiResponse)
def search_graph_nodes(
    query: str = Query(..., description="Search term for node names"),
    limit: int = Query(default=20, ge=1, le=100),
    controller: RecommendationController = Depends(_get_controller)
):
    """Search Knowledge Graph nodes by keyword."""
    return controller.search_graph_nodes(query, limit)


@router.get("/graph/node/{id}", response_model=ApiResponse)
def get_graph_node(
    id: str,
    controller: RecommendationController = Depends(_get_controller)
):
    """Fetch single node from Knowledge Graph by ID."""
    return controller.get_graph_node(id)
