import bodyParser, {type Request, type Response} from 'express'

export const post = [
  bodyParser.json(),
  async (req: Request, res: Response) => {
    if(req.method !== 'POST'){
      return res.status(405).send('Method Not Allowed');
    }

    if(!req.body.command){
      res.status(400).json({
        error: "The command is missing"
      })
    }


    const child = Bun.spawn(["./build.py", "--command", req.body.command, "--dir", process.env.BUILD_DIR], {
      cwd: "./lib",
      stdout: "pipe",
      stderr: "pipe",
    })

    for await (const chunk of child.stdout) {
      const lines = new TextDecoder().decode(chunk).split("\n")
      for (const line of lines) {
        console.log(line)
      }
    }

    await child.exited

    if(child.exitCode != 0){
      return res.status(500).send("Internal Server Error")
    }

    return res.status(200).send("Build was successfull!")
  }
]
