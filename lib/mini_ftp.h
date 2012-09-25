#ifndef _MINI_FTP
#define _MINI_FTP

/* 
 * miniftp ( static library)
 *
 * it maked by "mercury" in 2010-06-xx
 * this support only ftp retr command with binary active mode.
 *
 *
*/

#include <pthread.h>

class MiniFTP
{
public:
	MiniFTP();
	~MiniFTP();

	enum {FROM_DNS=0, FROM_IP};
	int DownloadFile(int type, const char *dev, const char *hostname, const char *filename, const char *ftp_id, const char *ftp_pass, const char *savefilename);
	int GetFile_Percent(); //return download percent
	void Cancel();

	static MiniFTP *getInstance();

private:
	void set_percent(int value);
	int percent;
	static MiniFTP *instance;

	int sockfd; // ftp socket
	unsigned short nPort;   //ftp port , now 21
	int Connect(int type, const char *hostname);
	int login(const char *ftp_id, const char *ftp_passwd);

	void cmd_send(const char *cmd, const char *argv);
	int Received_FromS();

	int FTPCMD_RETR(const char *filename, const char *savefilename);
	char port_args[50];

	unsigned short nDataPort; //data port
	void make_port();
	int data_sock;
	int client_sock;
	int Open_ActiveMode();
	int recv_file(int nSize, const char* filename);

	char hostip[50]; // hostip
	int GetLocalIP();
	int getIP(const char *dev);

	int FTPCMD_SIZE(const char *filename);
};

typedef struct _ftpdata
{
	MiniFTP *mini;
	int type;
	char dev[10]; //eth0, ra0, ...
	char hostname[50];
	char filename[50];
	char ftp_id[50];
	char ftp_pass[50];
	char savefilename[50];
	int flag;
}FTPDATA;

class MiniFTP_Thread
{
public:
	MiniFTP_Thread();
	~MiniFTP_Thread();

	enum {FROM_DNS=0, FROM_IP};

	int Alive_Check(int type, const char *hostname);
	static MiniFTP_Thread *getInstance();

	int DownloadFile(int type, const char *dev, const char *hostname, const char *filename, const char *ftp_id, const char *ftp_pass, const char *savefilename);

	int GetState();
	void Stop_Thread();
private:
	static MiniFTP_Thread *instance;
	static void* t_function(void* arg); 
	FTPDATA *ftpdata;
};

#endif
