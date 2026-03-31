/*
 * Copyright 2008-2009 the original author or authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package ocr.main.service;

import java.io.Serializable;

public class MainVO implements Serializable {

	private static final long serialVersionUID = 1L;


	private long ocr_col1;

	private String ocr_col2;

	public long getOcr_col1() {
		return ocr_col1;
	}

	public void setOcr_col1(long ocr_col1) {
		this.ocr_col1 = ocr_col1;
	}

	public String getOcr_col2() {
		return ocr_col2;
	}

	public void setOcr_col2(String ocr_col2) {
		this.ocr_col2 = ocr_col2;
	}


}
