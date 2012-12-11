#include <stdio.h>
#include <fcntl.h>
#include <time.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <net/if.h>
#include <sys/ioctl.h>
#include <stdlib.h>
#include <string.h>

//*************************************************************************
// 								DEFINE SECTION
//*************************************************************************

#define FALSE					0
#define TRUE					1

#define XAP_VENDOR				"shawpad"		// Default VENDOR
#define XAP_DEVICE				"xap-hub"		// Default DEVICE
#define XAP_INSTANCE			"heathub"			// Default INSTANCE
#define XAP_VENDOR_LEN			16				// Length for xAP address fields
#define XAP_DEVICE_LEN			16
#define XAP_INSTANCE_LEN		48
#define XAP_UID					"FF0003"		// Default UID
#define XAP_PORT				3639			// Default Port
#define XAP_HBEAT	 			60				// Default Heartbeat interval in secs

#define XAP_MAX_HUB_ENTRIES		50

#define XAP_MAX_MSG_ELEMENTS 	1000			// Consts for message parser
#define XAP_MAX_KEYNAME_LEN 	128
#define XAP_MAX_KEYVALUE_LEN 	1500
#define XAP_MAX_SECTION_LEN 	128

#define DEBUG_OFF 				0				// Debug levels
#define DEBUG_INFO 				1
#define DEBUG_VERBOSE 			2
#define DEBUG_DEBUG 			3

#define XMLGENERAL				"xap-hub.xml"	// General xml config file
#define TAGLENGTH				16				// Maximum length of xml tags
#define EVN_NAME_LEN			50				// Maximum length of xml event names
#define XML_LINE_LEN			120				// Maximum length of xml lines

#define MAX_QUEUE_BACKLOG 		5  				// number of connections that can queue (max. 5)

//*************************************************************************
// 								TYPEDEFS SECTION
//*************************************************************************

struct tg_xap_address {						// xAP address: Vendor.Device.Instance
	char vendor[XAP_VENDOR_LEN];			// Vendor name
	char device[XAP_DEVICE_LEN];			// Device
	char instance[XAP_INSTANCE_LEN];		// Instance
};

struct tg_xap_hubentry {
	int port; 								// ip-port to forward to
	int interval;
	int timer;
	int is_alive;
};

struct tg_xap_msg {							// Message elements struct
	char section[XAP_MAX_SECTION_LEN+1];
	char name[XAP_MAX_KEYNAME_LEN+1];
	char value[XAP_MAX_KEYVALUE_LEN+1];
};

//*************************************************************************
// 								GLOBAL VARIABLES
//				Accessible from anywhere within the application
//*************************************************************************

int g_debuglevel;							// 0=off, 1=info, 2=verbose, 3=debug

struct tg_xap_address g_xap_address;		// xAP address structure
char g_xap_uid[9];							// xAP UID
int g_xap_port;								// xAP Port
int g_xap_hbeat;							// xAP Heartbeat interval

struct tg_xap_msg g_xap_msg[XAP_MAX_MSG_ELEMENTS];	// xAP message elements
int g_xap_index;							// Index for xAP message elements array

struct tg_xap_hubentry g_xap_hubentry[XAP_MAX_HUB_ENTRIES];	// xAP-hub entry list

