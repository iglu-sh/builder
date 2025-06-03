import type {Request, Response} from 'express'
import raw from 'express'
import createRouter from "express-file-routing"
import ws from "express-ws"

const express = require("express")
const app = express()
const expressWs = require("express-ws")(app)

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

