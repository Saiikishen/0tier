CC = cc
CFLAGS = -I. -Werror=return-type
LDLIBS = -lpthread

HEADERS = sys_utils.h tap_utils.h
TARGETS = vport
VPORT_OBJS = vport.o tap_utils.o

all: $(TARGETS)

vport: $(VPORT_OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LDLIBS)

# Automatically rebuild .o files if headers change
vport.o: vport.c $(HEADERS)
	$(CC) $(CFLAGS) -c vport.c

tap_utils.o: tap_utils.c $(HEADERS)
	$(CC) $(CFLAGS) -c tap_utils.c

clean:
	rm -f $(VPORT_OBJS) $(TARGETS)
