from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timedelta
from app.database import get_db
from app.models.schemas import InviteLinkRedeem

router = APIRouter()

@router.post("/redeem")
async def redeem(body: InviteLinkRedeem, db: AsyncSession = Depends(get_db)):
    r = await db.execute(text("SELECT id,label,agent_name,plan,trial_days,is_vip FROM invite_links WHERE code=:c AND claimed_by IS NULL"),{"c":body.code})
    link = r.fetchone()
    if not link: raise HTTPException(404,"Invalid or claimed link")
    trial_end = None
    if not link[5] and link[4]:
        trial_end = datetime.utcnow() + timedelta(days=link[4])
    r2 = await db.execute(text("INSERT INTO user_profiles (phone_number,agent_name,plan,is_vip,trial_ends_at) VALUES (:p,:a,:pl,:v,:te) RETURNING id"),
        {"p":body.phone_number,"a":link[2],"pl":link[3] if not link[5] else "vip","v":link[5],"te":trial_end})
    uid = str(r2.fetchone()[0])
    await db.execute(text("UPDATE invite_links SET claimed_by=:uid,claimed_at=NOW() WHERE id=:lid"),{"uid":uid,"lid":link[0]})
    await db.execute(text("INSERT INTO activity_logs (user_id,action,details) VALUES (:uid,'onboarding',:det)"),{"uid":uid,"det":'{"plan":"'+link[3]+'"}'})
    return {"status":"ok","user_id":uid,"agent_name":link[2],"trial_ends_at":trial_end.isoformat() if trial_end else None,"is_vip":link[5]}
