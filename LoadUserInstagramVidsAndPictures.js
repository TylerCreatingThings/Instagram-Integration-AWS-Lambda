axios
.get(
    "https://graph.instagram.com/USERID/media?fields=id,username,media_url&access_token=TOKEN"
    .replace("USERID", this.instagramId)
    .replace("TOKEN", this.instagramAccessToken)
)
.then((response) => {
    for (var i = 0; i < response.data.data.length; i++) {
    if (
        response.data.data[i].media_url.includes("mp4") ||
        response.data.data[i].media_url.includes("ogg") ||
        response.data.data[i].media_url.includes("webm")
    ) {
        //default to mp4 for now... see what instagram defaults too or how to figure out dynamically
        this.videos.push({
        fileName: "instagram_" + response.data.data[i].id,
        src: response.data.data[i].media_url,
        fileType: "mp4",
        });
    } else {
        this.images.push({
        fileName: "instagram_" + response.data.data[i].id,
        src: response.data.data[i].media_url,
        });
    }
    }
})
.catch(() => {});