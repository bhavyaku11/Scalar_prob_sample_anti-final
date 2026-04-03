from fastapi import FastAPI
from models import Action
import json
import uvicorn
from env import DropshippingEnv

app = FastAPI(title="Dropshipping Operations Manager")
env = DropshippingEnv()

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Dropshipping Operations Manager API is running. Check /docs for endpoints."}

@app.post("/reset")
def reset_env():
    state_str = env.reset()
    return {"state": json.loads(state_str)}

@app.get("/state")
def get_state():
    state_str = env.state()
    return {"state": json.loads(state_str)}

@app.post("/step")
def step_env(req: Action):
    new_state, reward, done, info = env.step(req.action_str)
    return {
        "state": json.loads(new_state),
        "reward": reward,
        "done": done,
        "info": info
    }

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000)

def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()