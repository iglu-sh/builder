import bodyParser, {type Request, type Response} from 'express'
import { Validator } from 'jsonschema';

export const post = [
  bodyParser.json(),
  async (req: Request, res: Response) => {
    if(req.method !== 'POST'){
      return res.status(405).send('Method Not Allowed');
    }

    let validator = new Validator();
    const bodySchema = require("../../../schemas/bodySchema.json");
    let validate = validator.validate(req.body, bodySchema)


    if(!validate.valid){
      res.status(400).json({
        error: "JSON schema is not valid."
      })
    }

    const child = Bun.spawn(["./build.py", "--json", JSON.stringify(req.body)], {
      cwd: "./lib",
      stdout: "pipe",
      stderr: "pipe",
    })

    for await (const chunk of child.stdout) {
      const lines = new TextDecoder().decode(chunk).split("\n")
      for (const line of lines) {
        console.log("[STDOUT]:", line)
      }
    }

    await child.exited

    if(child.exitCode != 0){
      return res.status(500).send("Internal Server Error")
    }

    return res.status(200).send("Build was successfull!")
  }
]
