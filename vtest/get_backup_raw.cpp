// raw http support, not tested, use get_backup.cpp instead

#include <arpa/inet.h>
#include <iostream>
#include <unistd.h>
#include <sys/socket.h>
#include <cstdio>
#include <fstream>
#include <string>

#define BUFFER_SIZE 4096

int backup_file(char* filename) {

    // key = "backup"
    // it = iter(filename.lower())
    // return all(char in it for char in key.lower())
}

void append_file(const char* content, ssize_t bytes) {
    std::ofstream out("cat.png", std::ios::binary | std::ios::app);
    if (!out) {
        std::perror("writing failed");
        return;
    }
    out.write(content, bytes);
}

void open_file(const char* content, ssize_t bytes) {
    std::ofstream out("cat.png", std::ios::binary);
    if (!out) {
        std::perror("writing failed");
        return;
    }
    out.write(content, bytes);
}

const char* first_packet(char buffer[BUFFER_SIZE]) {
    std::string str(buffer);

    // find end of header
    const char* end_txt = "\r\n\r\n";
    size_t pos = str.find(end_txt);

    const char* content = str.substr(pos + strlen(end_txt)).c_str();
    return content;
}

int left_over(char buffer[BUFFER_SIZE], ssize_t bytes_read) {
    std::string str(buffer);

    // find end of header
    const char* end_txt = "\r\n\r\n";
    size_t pos = str.find(end_txt);

    int size = bytes_read - (pos + strlen(end_txt));
    return size;
}

int content_size(char buffer[BUFFER_SIZE]) {
    std::string str(buffer);

    // find content length
    const char* txt = "Content-Length:";
    size_t start_pos = str.find(txt);

    // ignore if content length doesn't exist in this packet
    if (start_pos == std::string::npos) 
        return -1;
       
    size_t size_start_pos = start_pos + strlen(txt);
    
    size_t end_pos = str.find("\r\n", size_start_pos);
    if (end_pos == std::string::npos) 
        return -1;

    int size = std::stoi(str.substr(size_start_pos, end_pos - size_start_pos));
    return size;
}

int main() {
    int soc = socket(AF_INET, SOCK_STREAM, 0);
    if (soc < 0)
        return -1;
    
    // server address
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = htons(8443);

    // bind socket with port
    if (bind(soc, (sockaddr*)&addr, sizeof(addr)) < 0) {
        std::perror("bind failed");
        return -1;
    }

    // listen to incoming packets
    if (listen(soc, 8) < 0) {
        std::perror("listen failed");
        close(soc);
        return -1;
    }
    
    // accept incoming packets
    int c_size = 0;
    int client_soc;
    while (true) {
        // read the first packet for content length
        client_soc = accept(soc, nullptr, nullptr);
        char buffer[BUFFER_SIZE] = {0};
        ssize_t bytes_read = read(client_soc, buffer, sizeof(buffer) - 1);
        c_size = content_size(buffer);
        if (c_size <= 0)
            continue;
        const char* content = first_packet(buffer);
        int left = left_over(buffer, bytes_read);
        open_file(content, left);
        c_size -= left;
        break;
    }
    
    // accept content packets
    while (c_size > 0) {
        if (client_soc >= 0) {
            // accept packet
            char buffer[BUFFER_SIZE] = {0};
            ssize_t bytes_read = read(client_soc, buffer, sizeof(buffer) - 1);
            if (bytes_read > 0) {
                // success, get the packet body
                append_file(buffer, bytes_read);
                c_size -= bytes_read;
            } else {
                // TODO: clean up the file
                return -1;
            }
        }
    }

    const char response[] =
        "HTTP/1.1 200 OK\r\n"
        "Content-Length: 8\r\n"
        "Connection: close\r\n"
        "\r\n"
        "received";
    
    if (send(client_soc, response, sizeof(response) - 1, 0) < 0)
        std::perror("send failed");

    close(soc);
    close(client_soc);
    return -1;
}