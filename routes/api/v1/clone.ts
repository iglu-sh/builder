import bodyParser, {type Request, type Response} from 'express'

export const post = [
  bodyParser.json(),
  async (req: Request, res: Response) => {
    if(req.method !== 'POST'){
      return res.status(405).send('Method Not Allowed');
    }

    if(!req.body.repo){
      res.status(400).json({
        error: "The repository is missing"
      })
    }

    const child = Bun.spawn(["./clone.py", "--repo", req.body.repo, "--dir", process.env.BUILD_DIR], {
      cwd: "./lib",
    })

    await child.exited

    if(child.exitCode != 0){
      return res.status(500).send("Internal Server Error")
    }

    return res.status(200).send("Git is cloned!")
  }
]
