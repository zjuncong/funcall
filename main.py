from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict
import uuid
import asyncio
import json
from app.agent import Agent

app = FastAPI(title="智能助手API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str

class ChatResponse(BaseModel):
    session_id: str
    message: str
    success: bool = True

session_agents: Dict[str, Agent] = {}

def get_or_create_agent(session_id: str) -> Agent:
    """获取或创建指定session的Agent实例"""
    if session_id not in session_agents:
        session_agents[session_id] = Agent()
        print(f"[系统] 为会话 {session_id} 创建新的Agent实例")
    return session_agents[session_id]

@app.get("/")
async def root():
    """API根路径，返回欢迎信息"""
    return {
        "message": "欢迎使用智能助手API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat",
            "sessions": "/sessions",
            "clear_session": "/clear/{session_id}",
            "docs": "/docs"
        }
    }

@app.get("/sessions")
async def list_sessions():
    """获取所有活跃会话"""
    return {
        "total": len(session_agents),
        "sessions": list(session_agents.keys())
    }

@app.delete("/clear/{session_id}")
async def clear_session(session_id: str):
    """清空指定会话的历史记录"""
    if session_id not in session_agents:
        raise HTTPException(status_code=404, detail="会话不存在")

    session_agents[session_id].clear_messages()
    return {"message": "会话已清空", "session_id": session_id}

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """删除指定会话"""
    if session_id not in session_agents:
        raise HTTPException(status_code=404, detail="会话不存在")

    del session_agents[session_id]
    return {"message": "会话已删除", "session_id": session_id}

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """流式聊天接口"""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="消息不能为空")

    session_id = request.session_id
    if not session_id:
        session_id = str(uuid.uuid4())

    agent = get_or_create_agent(session_id)

    async def event_generator():
        try:
            full_response = []

            for chunk in agent.chat_stream(request.message):
                if chunk:
                    full_response.append(chunk)

                    data = {
                        "type": "content",
                        "content": chunk,
                        "session_id": session_id
                    }
                    yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

                    await asyncio.sleep(0.01)

            final_response = "".join(full_response)

            data = {
                "type": "done",
                "content": final_response,
                "session_id": session_id
            }
            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

        except Exception as e:
            print(f"[错误] 流式响应出错: {e}")
            error_data = {
                "type": "error",
                "content": f"处理请求时出错: {str(e)}",
                "session_id": session_id
            }
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.post("/chat")
async def chat(request: ChatRequest):
    """非流式聊天接口（用于调试）"""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="消息不能为空")

    session_id = request.session_id
    if not session_id:
        session_id = str(uuid.uuid4())

    agent = get_or_create_agent(session_id)

    try:
        response = agent.chat(request.message)
        return {
            "session_id": session_id,
            "message": response,
            "success": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.mount("/static", StaticFiles(directory=".", html=True), name="static")

@app.get("/index.html")
async def index_html():
    """返回前端页面"""
    return FileResponse("index.html")

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🚀 启动智能助手API服务...")
    print("=" * 60)
    print("API地址: http://localhost:8001")
    print("文档地址: http://localhost:8001/docs")
    print("前端页面: http://localhost:8001/index.html")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)
