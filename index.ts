import type {Request, Response} from 'express'
import raw from 'express'
import createRouter from "express-file-routing"

// Check needed envs

const envs = [
  "BUILD_DIR"
]

envs.forEach(env => {
  if(!process.env[env]){
    console.error("env BUILD_DIR is missing")
    process.exit(1)
  }
})


const app = require('express')()

app.use(raw())

await createRouter(app, {
  additionalMethods: [ "ws" ]
})

app.use((req:Request, res:Response) => {
  console.log(req.url)
  console.log(req.method)
  console.log(req.headers)
})

app.listen(3000)


