/* xAP Compliant Hub

   Last changes:  28 March 2012 by Jose Luis Galindo (support@homected.com)
					code rewritten to adapt to work with RaspberryPi hardware.
   
   Last revision: 14 Dec 2002 by Patrick Lidstone


   Usage: xap-hub [<interface>] [<debug level>]

   e.g. xap-hub eth0 
		which uses interface eth0
   or   xap=hub
	    which uses default interface eth0

   <Debug level> = 0-off; 1-info; 2-verbose; 3-debug
   
   Copyright (c) Jose Luis Galindo, 2012.
   Copyright (c) Patrick Lidstone, 2002.
   
   No commercial use.
   No redistribution at profit.
   All derivative work must retain this message and
   acknowledge the work of the original author.  

   Please report defects to support@homected.com
   Original code from patrick@lidstone.net attached in zip file.

   Compile with supplied makefile
*/

#include "hub.h"


//*************************************************************************
//								APPLICATION FUNCTIONS 
//*************************************************************************

short int xmlReadGeneral(void) {
	FILE *fpXml;					// Pointer to xml file
	char strLine[XML_LINE_LEN];		// XML read buffer
	char *pStr1, *pStr2;			// Pointers to strings
	short int intCheck = 0;			// Checks the existence and order of tags in the xml file
	int flgEndLoop = FALSE;			// Condition to exit the main read loop
	int intLen = 0;					// Length of strings
	char strBuf[TAGLENGTH+3];		// Temporary buffer
	char strKey[TAGLENGTH];			// Keyword buffer
	char strValue[XML_LINE_LEN];	// Value buffer

	// Open the xml file in read-only mode
	if ((fpXml = fopen(XMLGENERAL, "r")) == NULL)
		return FALSE;	// File not found

	// Read lines from the xml file
	while (fgets(strLine, sizeof(strLine), fpXml) != NULL && !flgEndLoop)
	{
		pStr1 = strLine;		// Pointer at the beginning of the line

		// Skip initial paddings
		while(pStr1[0] == '\t' || pStr1[0] == ' ')
			pStr1++;

		// Inspect the captured line
		switch(intCheck) {
			case 0:	// xml file header?
				if (!strcmp(pStr1, "<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n"))
					intCheck = 1;						// This tag is mandatory
				break;

			case 1:	// "device" start tag?
				if (!strcmp(pStr1, "<device>\n"))
					intCheck = 2;						// This tag is mandatory
				break;
			
			case 2:	// Inside the "device" section
				if (pStr1[0] == '<') {
					pStr1++;											// Skip the "<"
					// Capture the keyword string
					if ((pStr2 = strchr(pStr1, '>')) != NULL) {
						pStr2[0] = 0;
						if (strlen(pStr1) < sizeof(strKey)) {			// Avoid exceeding the size of the target buffer
							strcpy(strKey, pStr1);						// Copy the keyword string

							// "device" end tag?
							if (strKey[0] == '/') {
								if (!strcmp(strKey, "/device"))
									return TRUE;							// End of the read process. Exit the function
							}

							sprintf(strBuf, "</%s>", strKey);			// This should be the end tag string
							pStr1 = pStr2 + 1;
							
							// Capture the field value (search the end tag string)
							if ((pStr2 = strstr(pStr1, strBuf)) != NULL) {
								pStr2[0] = 0;
								intLen = strlen(pStr1);
								if (intLen < sizeof(strValue)) {		// Avoid exceeding the size of the target buffer
									strcpy(strValue, pStr1);			// Copy the value string
							
									// Depending of the tag string
									switch(strKey[0]) {
										case 'n':												// If "<name>" (instance name) tag
											if (!strcmp(strKey, "name")) {
												if (intLen < sizeof(g_xap_address.instance))	// Avoid exceeding the target buffer
													strcpy(g_xap_address.instance, strValue);	// Store the instance (name)
											}
											break;
											
										case 'p':												// If "<port>" tag
											if (!strcmp(strKey, "port"))
												g_xap_port = atoi(strValue);					// Store the port
											break;
											
										case 'x':
											if (!strcmp(strKey, "xaphbeatf"))					// If "<xaphbeatf>" (xAP heartbeat frequency) tag
												g_xap_hbeat = atoi(strValue);					// Frequency in seconds
											else if (!strcmp(strKey, "xapuid")) {				// If "<xapuid>" (xAP base UID) tag
												if (intLen < sizeof(g_xap_uid))					// Avoid exceeding the target buffer
													strcpy(g_xap_uid, strValue);				// Store the base UID
											}
											break;
											
										default:
											break;
									}
								}
							}
						}
					}
				}
				break;
			default:
				break;
		}
	}

	return FALSE;
}

void xaphub_build_heartbeat(char* a_buff) {
	sprintf(a_buff, "xap-hbeat\n{\nv=12\nhop=1\nuid=%s00\nclass=xap-hbeat.alive\nsource=%s.%s.%s\ninterval=%d\nport=%d\n}\n", g_xap_uid, g_xap_address.vendor, g_xap_address.device,  g_xap_address.instance, g_xap_hbeat, g_xap_port);
		
	if (g_debuglevel >= DEBUG_VERBOSE) {
		printf("Heartbeat source=%s, instance=%s, interval=%d, port=%d\n",g_xap_address.device, g_xap_address.instance, g_xap_hbeat, g_xap_port);
	}
}

int xaphub_init() {
	
	// Load default values
	strcpy(g_xap_address.vendor, XAP_VENDOR);		// Vendor name is a constant string
	strcpy(g_xap_address.device, XAP_DEVICE);		// Device name is a constant string
	strcpy(g_xap_address.instance, XAP_INSTANCE);	// Default instance name
	strcpy(g_xap_uid, XAP_UID);						// Default UID
	g_xap_port = XAP_PORT;							// Default Port
	g_xap_hbeat = XAP_HBEAT;						// Default heartbeat interval
	
	// Initialize hub entries
	int i;
	for (i = 0; i < XAP_MAX_HUB_ENTRIES; i++) {
		g_xap_hubentry[i].is_alive=0;
	}
	return 1;
}

int xaphub_addentry(int a_port, int a_interval) {
	
	// add new or update existing hub entry, resetting countdown timer
	int i;
	int matched;

	matched = XAP_MAX_HUB_ENTRIES;

	for (i = 0; i < XAP_MAX_HUB_ENTRIES; i++) {
		if (g_xap_hubentry[i].port == a_port) {
			// entry exists, update it
			g_xap_hubentry[i].interval = a_interval;
			g_xap_hubentry[i].timer = a_interval * 2;
			g_xap_hubentry[i].is_alive = 1;
			matched = i;
			if (g_debuglevel >= DEBUG_VERBOSE) {
				printf("Heartbeat for port %d\n", g_xap_hubentry[i].port);
			}
			break;
		}
	}
	
	if (matched == XAP_MAX_HUB_ENTRIES) {
		// no entry exists, create a new entry in first free slot
		for (i = 0; i < XAP_MAX_HUB_ENTRIES; i++) {
			if (g_xap_hubentry[i].is_alive == 0) {
				// free entry exists, use it it
				g_xap_hubentry[i].port = a_port;
				g_xap_hubentry[i].interval = a_interval;
				g_xap_hubentry[i].timer = a_interval * 2;
				g_xap_hubentry[i].is_alive = 1;
				matched = i;
				if (g_debuglevel >= DEBUG_INFO) {
					printf("Connecting port %d\n", g_xap_hubentry[i].port);
				}
				break;
			}
		}
	}
	return matched; // value of XAP_MAX_HUB_ENTRIES indicates list full
}

void xaphub_tick(time_t a_interval) {
	// Called regularly. a_interval specifies number of whole seconds elapsed since last call.
	int i;

	for (i=0; i < XAP_MAX_HUB_ENTRIES; i++) {
		// update timer entries. If timer is 0 then ignore hearbeat ticks
		if ((g_xap_hubentry[i].is_alive) && (g_xap_hubentry[i].timer != 0)) {
			g_xap_hubentry[i].timer -= a_interval;

			if (g_xap_hubentry[i].timer <= 0) {
				if (g_debuglevel >= DEBUG_INFO) {
					printf("Disconnecting port %d due to loss of heartbeat\n", g_xap_hubentry[i].port);
				}
				g_xap_hubentry[i].is_alive = 0; // mark as idle
			}
			break;
		}
	}
}

int xaphub_relay(int a_txsock, const char* a_buf) {

	struct sockaddr_in tx_addr;
	int i, j = 0;

	memset((char *) &tx_addr, 0, sizeof(tx_addr));
	tx_addr.sin_family = AF_INET;		
	tx_addr.sin_addr.s_addr = inet_addr("127.0.0.1");

	for (i=0; i < XAP_MAX_HUB_ENTRIES; i++) {
		if (g_xap_hubentry[i].is_alive == 1) {
			// entry exists, use it
			if (g_debuglevel >= DEBUG_VERBOSE) {
				printf("Relayed to %d\n", g_xap_hubentry[i].port);
			}
			j++;
			tx_addr.sin_port = htons(g_xap_hubentry[i].port);
			sendto(a_txsock, a_buf, strlen(a_buf), 0, (struct sockaddr*)&tx_addr, sizeof(struct sockaddr_in));	
		}
	}
	return j; // number of connected hosts we relayed to
}

int xapmsg_parse(const char* a_buffer) {

	// Parse incoming message.

	auto int i_cursor=0;
	auto int i;
	auto int i_state;

	char i_keyname[XAP_MAX_KEYNAME_LEN+1];
	char i_keyvalue[XAP_MAX_KEYVALUE_LEN+1];
	char i_section[XAP_MAX_SECTION_LEN+1];

	#define START_SECTION_NAME 0
	#define IN_SECTION_NAME    1
	#define START_KEYNAME      2
	#define IN_KEYNAME         3
	#define START_KEYVALUE     4
	#define IN_KEYVALUE        5

	i_state = START_SECTION_NAME;
	g_xap_index = 0;

	for (i=0; i < strlen(a_buffer); i++) {
		switch (i_state) {
			case START_SECTION_NAME:
				if ((a_buffer[i]>32) && (a_buffer[i]<128)) {
					i_state ++;
					i_cursor=0;
					i_section[i_cursor++]=a_buffer[i];
				}
				break;

			case IN_SECTION_NAME:
				if (a_buffer[i]!='{') {
					if (i_cursor < XAP_MAX_SECTION_LEN) i_section[i_cursor++] = a_buffer[i];
				}
				else {
					while (i_section[i_cursor-1] <= 32) {
						i_cursor--; // remove possible single trailing space
					}
					i_section[i_cursor] = '\0';
					i_state++;
				}
				break;

			case START_KEYNAME:
				if (a_buffer[i]=='}') {
					i_state=START_SECTION_NAME; // end of this section
					}
				else
				if ((a_buffer[i] > 32) && (a_buffer[i] < 128)) {
					i_state ++;
					i_cursor=0;
					if (i_cursor < XAP_MAX_KEYNAME_LEN) 
						i_keyname[i_cursor++] = a_buffer[i];
				}
				break;

			case IN_KEYNAME:
				// Key name starts with printable character, ends with printable character
				// but may include embedded spaces
				if ((a_buffer[i]>=32) && (a_buffer[i]!='=')) {
					i_keyname[i_cursor++]=a_buffer[i];
				}
				else {
					if (i_keyname[i_cursor-1]==' ') 
						i_cursor--; // remove possible single trailing space
					i_keyname[i_cursor]='\0';
					i_state++;
				}
				break;

			case START_KEYVALUE:
				if ((a_buffer[i]>32) && (a_buffer[i]<128)) {
					i_state ++;
					i_cursor=0;
					if (i_cursor<XAP_MAX_KEYVALUE_LEN) 
						i_keyvalue[i_cursor++]=a_buffer[i];
				}
				break;

			case IN_KEYVALUE:
				if (a_buffer[i]>=32) {
					i_keyvalue[i_cursor++]=a_buffer[i];
				}
				else { // end of key value pair
				
					i_keyvalue[i_cursor]='\0';
					i_state=START_KEYNAME;

					strcpy(g_xap_msg[g_xap_index].section, i_section);
					strcpy(g_xap_msg[g_xap_index].name, i_keyname);
					strcpy(g_xap_msg[g_xap_index].value, i_keyvalue);
					if (g_debuglevel >= DEBUG_VERBOSE) {
						printf("XAPLIB Msg: Name=<%s:%s>, Value=<%s>\n",g_xap_msg[g_xap_index].section, g_xap_msg[g_xap_index].name, g_xap_msg[g_xap_index].value);
					}
					g_xap_index++;
					
					if (g_xap_index > XAP_MAX_MSG_ELEMENTS) {
						g_xap_index = 0;
						printf("XAPLIB Warning: data lost (message too big)\n");
					}
				}
				break;
		} // switch
	} // for
	return g_xap_index;
} // parse

int xapmsg_getvalue(const char* a_keyname, char* a_keyvalue) {

	// Retrieve a keyvalue in form <section>:<keyvalue>
	// Return 1 on success, 0 on failure

	auto int i;
	auto int matched;
	char i_composite_name[XAP_MAX_SECTION_LEN+XAP_MAX_KEYVALUE_LEN+1];

	i=0;
	matched=0;

	while ((!matched) && (i++<g_xap_index)) {
		strcpy(i_composite_name, g_xap_msg[i-1].section);
		strcat(i_composite_name,":");
		strcat(i_composite_name, g_xap_msg[i-1].name);
		if (strcasecmp(i_composite_name, a_keyname)==0) {
			matched=1;
			strcpy(a_keyvalue, g_xap_msg[i-1].value);
		} // if
	} // while
	return matched;
} // getvalue

void xap_handler(const char* a_buf) {
	
	char i_interval[16];
	char i_port[16];

	xapmsg_parse(a_buf);

	if (xapmsg_getvalue("xap-hbeat:interval", i_interval) == 0) {
		if (g_debuglevel >= DEBUG_DEBUG) {
			printf("Could not find <%s> in message\n","xap-hbeat.interval"); 
		}
	} 
	else {
		if (xapmsg_getvalue("xap-hbeat:port", i_port) == 0) {
			if (g_debuglevel >= DEBUG_DEBUG) {
				printf("Could not find <%s> in message\n","xap-hbeat:port"); 
			}
		} 
		else {
			// Add entry if port is not my self
			if(atoi(i_port) != g_xap_port)
				xaphub_addentry(atoi(i_port), atoi(i_interval));
		}
	}
}

//*************************************************************************
//								MAIN PROGRAM 
//*************************************************************************

int main(int argc, char* argv[]) {

	char interfacename[20];						// Hardware interface name (eth0, ...)
	struct ifreq interface;						// ioctls to configure network interface
	
	struct sockaddr_in myinterface;				// Interface address
	struct sockaddr_in mynetmask;				// Interface netmask
	struct sockaddr_in mybroadcast;				// Interface broadcast address
	
	int server_sockfd;							// Server socket
	struct sockaddr_in server_address;			// Server address and port
	int heartbeat_sockfd;						// Heartbeat socket
	struct sockaddr_in heartbeat_addr;			// Heartbeat address and port
	int tx_sockfd;								// Tx socket
	int optval, optlen;							// Vars for socket options
		
	time_t timenow;								// Current time
	time_t xaptick;								// Last tick
	time_t heartbeattick;						// Time for next hearbeat tick
	
	char heartbeat_msg[1500];					// Buffer for heartbeat messages
	char buff[1500];							// Buffer for messages
	
	fd_set rdfs;								// Vars for attent to clients
	struct timeval tv;
	struct sockaddr_in client_address;			// 	client address and port
	socklen_t client_len;
		
	int i; 										// Auxiliary variable

	// Header verbage
	printf("\nHomected xAP-Hub Connector\n");
	printf("Copyright (C) Jose Luis Galindo, 2012\n");
	
	// Initialize xAP-hub
	xaphub_init();
	
	// Load xml file with general settings
	if (xmlReadGeneral())
		printf("Settings from xml file loaded\n");
	else
		printf("Xml file not found, default settings loaded\n");

	// Apply arguments from command line
	if (argc<2) {
		// set default interface
		strcpy(interfacename, "eth0");
	} 
	else {
		// get chosen interface
		strncpy(interfacename, argv[1], sizeof(interfacename)-1);
	}
	if (argc<3) {
		// set default debug level
		g_debuglevel = DEBUG_OFF;
	}
	else {
		g_debuglevel=atoi(argv[2]);
	}

	// Use the server socket to get interface properties
	server_sockfd = socket(AF_INET, SOCK_DGRAM, 0);
	if (server_sockfd == -1) {
		printf("Error trying to get interface properties\n");
		return 0;
	}

	// Set options for the socket
	optval=1;
	optlen=sizeof(int);
	if (setsockopt(server_sockfd, SOL_SOCKET, SO_BROADCAST, (char*)&optval, optlen)) {
		printf("Error trying to get interface properties\n");
		return 0;
	}
	
	optval=1;
	optlen=sizeof(int);
	if (setsockopt(server_sockfd, SOL_SOCKET, SO_REUSEADDR, (char*)&optval, optlen)) {
		printf("Error trying to get interface properties\n");
		return 0;
	}

	// Query the low-level capabilities of the network interface to get address and netmask
	memset((char*)&interface, sizeof(interface),0);
	strcpy(interface.ifr_name, interfacename);
	
	// Get the interface address
	interface.ifr_addr.sa_family = AF_INET; 
	if (ioctl(server_sockfd, SIOCGIFADDR, &interface) != 0) {
		printf("Could not determine IP address for interface %s\n", interfacename);
		return 0;
	}
	myinterface.sin_addr.s_addr = ((struct sockaddr_in*)&interface.ifr_broadaddr)->sin_addr.s_addr;
	if (g_debuglevel >= DEBUG_INFO) {
		printf("%s: address %s\n", interface.ifr_name, inet_ntoa(((struct sockaddr_in*)&interface.ifr_addr)->sin_addr));
	}
	
	// Get the interface netmask
	interface.ifr_broadaddr.sa_family = AF_INET; 
	if (ioctl(server_sockfd, SIOCGIFNETMASK, &interface) != 0) {
		printf("Unable to determine netmask for interface %s\n", interfacename);
		return 0;
	}
	mynetmask.sin_addr.s_addr = ((struct sockaddr_in*)&interface.ifr_broadaddr)->sin_addr.s_addr;
	if (g_debuglevel >= DEBUG_INFO) {
		printf("%s: netmask %s\n", interface.ifr_name, inet_ntoa(((struct sockaddr_in*)&interface.ifr_netmask)->sin_addr));
	}
	
	// Determine the interface broadcast address 
	long int inverted_netmask;
	inverted_netmask=~mynetmask.sin_addr.s_addr;
	mybroadcast.sin_addr.s_addr = inverted_netmask | myinterface.sin_addr.s_addr;
	if (g_debuglevel >= DEBUG_INFO) {
		printf("%s: broadcast %s\n", interface.ifr_name, inet_ntoa(mybroadcast.sin_addr));
	}

	// Set the server socket
	server_sockfd = socket(AF_INET, SOCK_DGRAM, 0);
	
	// Set server address and port
	memset((char *) &server_address, 0, sizeof(server_address));
	server_address.sin_family = AF_INET; 	
	server_address.sin_addr.s_addr = htonl(INADDR_ANY);	// Receive from any address
	server_address.sin_port = htons(g_xap_port);		// on this port (Default 3639)
	
	// Bind the server socket with the server IP address and port
	fcntl(server_sockfd, F_SETFL, O_NONBLOCK);
	if (bind(server_sockfd, (struct sockaddr*)&server_address, sizeof(server_address)) !=0 ) {
		// if fails then we can assume that a hub is active on this host
		printf("Port %d is in use\n", g_xap_port);
		printf("Assuming other local hub is active on this host\n");		
		return 0;
	}
	else {
		if (g_debuglevel >= DEBUG_INFO) {
			printf("Listening for messages on port %d\n", g_xap_port);
		}
	}

	// Set the server socket to listen
	listen(server_sockfd, MAX_QUEUE_BACKLOG);
	
	// Set up the Tx socket
	tx_sockfd = socket(AF_INET, SOCK_DGRAM, 0);

	// Set up the heartbeat socket, on which we tell the world we are alive and well
	heartbeat_sockfd = socket(AF_INET, SOCK_DGRAM, 0);
	if (heartbeat_sockfd == -1) {
		printf("Heartbeat socket cannot be created\n");
		return 0;
	}
	
	// Set options for the heartbeat socket
	optval = 1;
    optlen = sizeof(int);
    if (setsockopt(heartbeat_sockfd, SOL_SOCKET, SO_BROADCAST, (char*)&optval, optlen)) {
	   printf("Unable to set heartbeat socket options\n");
	   return 0;
	}
	
	// Set up heartbeat address and port
	memset((char *) &heartbeat_addr, 0, sizeof(heartbeat_addr));
	heartbeat_addr.sin_family = AF_INET;
	heartbeat_addr.sin_port = htons(g_xap_port);
	heartbeat_addr.sin_addr.s_addr = mybroadcast.sin_addr.s_addr;
	if (g_debuglevel >= DEBUG_INFO) {
		printf("Set heartbeat broadcast on %s:%d\n", inet_ntoa(heartbeat_addr.sin_addr), g_xap_port);
	}

	xaptick = time((time_t*)0);
	heartbeattick = time((time_t*)0); // force heartbeat on startup
	printf("Running...\n");

	// Parse heartbeat messages received on broadcast interface
	// If they originated from this host, add the port number to the list of known ports
	// Otherwise ignore.
	// If ordinary header then pass to all known listeners	
	while (1)
	{
		// Get current time
		timenow = time((time_t*)0);
		
		// Hub tick, check for alive devices
		if (timenow - xaptick >= 1) {
			if (g_debuglevel >= DEBUG_DEBUG) {
				printf("XAP Connection list tick %d\n", (int)timenow - (int)xaptick);
			}
			xaphub_tick(timenow - xaptick);
			xaptick = timenow;
		}
		
		// Heartbeat tick
		if (timenow >= heartbeattick) {
			if (g_debuglevel >= DEBUG_DEBUG) {
				printf("Outgoing heartbeat tick %d\n",(int)timenow);
			}
			
			// Create the heartbeat message
			xaphub_build_heartbeat(heartbeat_msg);
			if (g_debuglevel >= DEBUG_DEBUG) {
				printf("%s", heartbeat_msg);
			}

			// Send heartbeat to all external listeners
			sendto(heartbeat_sockfd, heartbeat_msg, strlen(heartbeat_msg), 0, (struct sockaddr *) &heartbeat_addr, sizeof(heartbeat_addr));
			if (g_debuglevel >= DEBUG_VERBOSE) {
				printf("Broadcasting heartbeat\n");
			}

			// Send heartbeat to all locally connected apps
			xaphub_relay(tx_sockfd, heartbeat_msg);
			
			// Set next tick
			heartbeattick = timenow + g_xap_hbeat;
		}
		
		// Prepare to attent to the clients
		FD_ZERO(&rdfs);
		FD_SET(server_sockfd, &rdfs);
		tv.tv_sec = g_xap_hbeat;
		tv.tv_usec = 0;
		select(server_sockfd + 1, &rdfs, NULL, NULL, &tv);
		
		// Select either timed out, or there was data - go look for it.
		client_len = sizeof(struct sockaddr);
		i = recvfrom(server_sockfd, buff, sizeof(buff), 0, (struct sockaddr*) &client_address, &client_len);

		// Check if a message was received
		if (i != -1) {
			buff[i]='\0';	// Add NULL to the end of message
		
			if (g_debuglevel >= DEBUG_VERBOSE) {
				printf("Message from client %s:%d\n", inet_ntoa(client_address.sin_addr), ntohs(client_address.sin_port));
			}
			
			// Message from my interface
			if (client_address.sin_addr.s_addr == myinterface.sin_addr.s_addr) {
				if (g_debuglevel >= DEBUG_VERBOSE) {
					printf("Message originated from my interface\n");
				}
				// If the message received is a heartbeat message, add the client to the relay list
				xap_handler(buff);
					
				// Relay the message to all local apps, the originator will see his own message
				xaphub_relay(tx_sockfd, buff);
			}
			// Message from local client received
			else if (client_address.sin_addr.s_addr == inet_addr("127.0.0.1")) {
				if (g_debuglevel >= DEBUG_VERBOSE) {
					printf("Message from local client\n");
				}
			}
			// Remote message
			else {
				if (g_debuglevel >= DEBUG_VERBOSE) {
					printf("Message originated remotely, relay\n");
				}
				// Relay the message to all local apps
				xaphub_relay(tx_sockfd, buff);
			}
		}
	}
}	// main
