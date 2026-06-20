export function createPythonServerUrls(pyServer) {
  const baseUrl = pyServer.replace(/\/$/, "");

  return {
    videoFeedUrl: `${baseUrl}/video_feed`,
    wsUrl: `${baseUrl.replace(/^http/, "ws")}/ws`,
  };
}

export function formatCommandTime(isoTimestamp) {
  return new Date(isoTimestamp).toLocaleTimeString();
}
