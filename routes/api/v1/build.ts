import bodyParser, {type Request, type Response} from 'express'

export const post = [
  bodyParser.json(),
  async (req: Request, res: Response) => {
    if(req.method !== 'POST'){
      return res.status(405).send('Method Not Allowed');
    }

    if(!req.query.command){
      res.status(400).json({
        error: "The command is missing"
      })
    }

    const child = Bun.spawn(["./build.py", "--command", req.query.command, "--dir", process.env.BUILD_DIR], {
      cwd: "./lib",
    })

    await child.exited
    let stdout = await new Response(child.stdout).text()

    console.log("HIER: ", stdout);

    if(child.exitCode != 0){
      return res.status(500).send("Internal Server Error")
    }

    return res.status(200).send("Build was successfull!")
  }
]
