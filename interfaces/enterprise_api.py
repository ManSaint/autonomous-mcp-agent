.server_name,
                            "tool": req.tool_name,
                            "success": False,
                            "error": str(e)
                        })
                
                successful = len([r for r in results if r["success"]])
                
                self._track_api_request("batch_execute", True)
                return APIResponse(
                    success=True,
                    data={
                        "results": results,
                        "summary": {
                            "total": len(requests),
                            "successful": successful,
                            "failed": len(requests) - successful
                        }
                    },
                    message=f"Batch execution completed: {successful}/{len(requests)} successful"
                )
                
            except HTTPException:
                self._track_api_request("batch_execute", False)
                raise
            except Exception as e:
                self._track_api_request("batch_execute", False)
                raise HTTPException(status_code=500, detail=str(e))
    
    async def start_server(self, host: str = "localhost", port: int = 8001):
        """Start the API server"""
        try:
            self.logger.info(f"🚀 Starting Enterprise API on {host}:{port}")
            
            # Initialize all components first
            await self.initialize()
            
            # Start the server
            config = uvicorn.Config(
                app=self.app,
                host=host,
                port=port,
                log_level="info"
            )
            server = uvicorn.Server(config)
            await server.serve()
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start API server: {str(e)}")
            raise

# Standalone API launcher
async def launch_enterprise_api():
    """Launch the enterprise API"""
    api = EnterpriseAPI()
    await api.start_server()

if __name__ == "__main__":
    asyncio.run(launch_enterprise_api())
