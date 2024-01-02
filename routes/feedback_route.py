from fastapi import APIRouter, HTTPException
from models.feedback_model import FeedbackInput
from services.feedback_service import write_feedback

router = APIRouter(prefix = '/feedback', tags=["Feedback"])

@router.post('/')    
async def submit_feedback(feedback_input: FeedbackInput):
    try:
        feedback_response = write_feedback(
            feedback_input.mission_id,
            feedback_input.user_comment,
            feedback_input.rating,
            feedback_input.prompt_version
        )
        return {"message": "Feedback submitted successfully", "feedback_id": feedback_response["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))