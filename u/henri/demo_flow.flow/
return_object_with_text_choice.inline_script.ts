// import * as wmill from "windmill-client"

export async function main(x: string) {
  return {choices: [{text: x}]};
}
