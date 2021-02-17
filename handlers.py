import image as im

@app.event('file_shared')
def file_shared(body, client, context, logger):
    file_id = body["event"]["file_id"]
    file_info = client.files_info(file=file_id)

    if file_info['file']['filetype'] not in ['jpg']:
        return

    url = file_info['file']['url_private']

    image = im.open_url(url, token)

    mirrored = im.mirror(image)
    mirrored.save('/tmp/%s.jpg'%file_id)

    with open('/tmp/%s.jpg'%file_id, 'rb') as file_content:
        response = client.files_upload(
            file=file_content,
            channels="sapsik"
            )

