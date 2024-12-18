import * as wmill from 'windmill-client';
import { S3Object } from 'windmill-client';

export async function main(input_file: S3Object) {
	// Load the entire file_content as a Uint8Array
	const file_content = await wmill.loadS3File(input_file);

	const decoder = new TextDecoder();
	const file_content_str = decoder.decode(file_content);
	console.log(file_content_str);
}