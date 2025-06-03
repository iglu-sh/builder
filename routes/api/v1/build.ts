import bodyParser, {type Request, type Response} from 'express'
import { Validator } from 'jsonschema'
import type ExpressWs from 'express-ws'
import fs from 'node:fs'

let validator = new Validator();
const bodySchema = require("../../../schemas/bodySchema.json");

export const post = [
  bodyParser.json(),
  async (req: Request, res: Response) => {
    if(req.method !== 'POST'){
      return res.status(405).send('Method Not Allowed');
    }

    let validate = validator.validate(req.body, bodySchema)


    if(!validate.valid){
      res.status(400).json({
        error: "JSON schema is not valid."
      })
    }

    const child = Bun.spawn([Bun.main.split("/").slice(0, -1)?.join("/") + "/lib/build.py", "--json", JSON.stringify(req.body)])

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

export const ws = async (ws:ExpressWs, req:object) => {
  async function start_build(job:Object){
    ws.send("Start building...")
    console.log(Bun.main.split("/").slice(0, -1))
    const child = Bun.spawn([Bun.main.split("/").slice(0, -1)?.join("/") + "/lib/build.py", "--json", JSON.stringify(job)])

    for await (const chunk of child.stdout) {
      const lines = new TextDecoder().decode(chunk).split("\n")
      for (const line of lines) {
        if(line !== ""){
          console.log("[STDOUT]:", line)
          ws.send("[STDOUT]: " + line)
        }
      }
    }

    await child.exited

    if(child.exitCode != 0){
      ws.send("Internal Server Error")
      ws.close()
    }

    ws.send("Build was successfull!")
    ws.close()
  }

  ws.on('message', function(msg:string){
    try{
      const job = JSON.parse(msg)
      let validate = validator.validate(job, bodySchema)
      if(!validate.valid){
        ws.send(JSON.stringify({error: "JSON schema is not valid."}))
        ws.close()
      }else{
        start_build(job)
      }
    }catch(e){
      ws.send("Not a valid JSON")
      ws.close()
    }
  })
}
