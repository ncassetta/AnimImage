void print_lzw_table(struct myvector *table);
void print_codes_table(struct myvector *table);
void print_uint16_string(struct myvector *table);

void* LZWAlgorythm(unsigned int lzw_code_size, unsigned int len, unsigned char* bytes);
